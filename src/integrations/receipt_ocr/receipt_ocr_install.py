from __future__ import annotations

import importlib
import sys
from collections.abc import Callable, Sequence
from subprocess import CompletedProcess, TimeoutExpired
from subprocess import run as subprocess_run

MACOS_OCR_PACKAGES: tuple[str, ...] = (
    "pyobjc-framework-Vision",
    "pyobjc-framework-Cocoa",
)
WINDOWS_OCR_PACKAGES: tuple[str, ...] = (
    "winrt-Windows.Media.Ocr[all]",
    "winrt-Windows.Graphics.Imaging[all]",
    "winrt-Windows.Storage[all]",
    "winrt-Windows.Storage.Streams[all]",
)
LINUX_OCR_PACKAGES: tuple[str, ...] = (
    "pytesseract",
    "pillow",
)
_INSTALL_TIMEOUT_SECONDS = 180
_TESSERACT_ENGINE_MISSING = (
    "Python Tesseract bindings are installed, but the Tesseract engine was not found. "
    "Install it with your package manager (for example: apt install tesseract-ocr) "
    "and try Scan again."
)
_STILL_UNAVAILABLE = (
    "Installed OCR packages but scanning is still unavailable. Restart the app and try Scan again."
)


class ReceiptOcrInstallError(OSError):
    """Raised when on-device OCR bindings cannot be installed."""


def is_frozen_runtime() -> bool:
    return bool(getattr(sys, "frozen", False))


def ocr_platform_id(platform: str | None = None) -> str:
    host = sys.platform if platform is None else platform
    if host == "darwin":
        return "macos"
    if host == "win32":
        return "windows"
    if host.startswith("linux"):
        return "linux"
    return "other"


def is_supported_ocr_platform(*, platform: str | None = None) -> bool:
    return ocr_platform_id(platform) != "other"


def ocr_pip_packages(*, platform: str | None = None) -> tuple[str, ...]:
    kind = ocr_platform_id(platform)
    if kind == "macos":
        return MACOS_OCR_PACKAGES
    if kind == "windows":
        return WINDOWS_OCR_PACKAGES
    if kind == "linux":
        return LINUX_OCR_PACKAGES
    return ()


def can_install_receipt_ocr(*, platform: str | None = None, frozen: bool | None = None) -> bool:
    """True when pip can add on-device OCR bindings to this interpreter."""
    is_frozen = is_frozen_runtime() if frozen is None else frozen
    return is_supported_ocr_platform(platform=platform) and not is_frozen


def install_receipt_ocr_bindings(
    *,
    platform: str | None = None,
    frozen: bool | None = None,
    python_executable: str | None = None,
    run: Callable[..., CompletedProcess[str]] | None = None,
    ocr_available: Callable[[], bool] | None = None,
) -> None:
    """Install platform OCR bindings into the running interpreter."""
    host = sys.platform if platform is None else platform
    if not can_install_receipt_ocr(platform=host, frozen=frozen):
        if not is_supported_ocr_platform(platform=host):
            msg = "On-device receipt scanning is not available on this platform."
            raise ReceiptOcrInstallError(msg)
        msg = "On-device receipt scanning cannot be installed in this app build."
        raise ReceiptOcrInstallError(msg)

    packages = ocr_pip_packages(platform=host)
    python = python_executable if python_executable is not None else sys.executable
    runner = run if run is not None else subprocess_run
    args: Sequence[str] = (python, "-m", "pip", "install", *packages)
    try:
        result = runner(
            list(args),
            capture_output=True,
            text=True,
            timeout=_INSTALL_TIMEOUT_SECONDS,
            check=False,
        )
    except FileNotFoundError as exc:
        msg = (
            "Could not install on-device receipt scanning. "
            "Check your network connection and try again."
        )
        raise ReceiptOcrInstallError(msg) from exc
    except TimeoutExpired as exc:
        msg = "Installing on-device receipt scanning timed out. Check your network and try again."
        raise ReceiptOcrInstallError(msg) from exc

    if result.returncode != 0:
        detail = _pip_failure_detail(result)
        msg = f"Could not install on-device receipt scanning: {detail}"
        raise ReceiptOcrInstallError(msg)

    importlib.invalidate_caches()
    available = (
        ocr_available if ocr_available is not None else (lambda: _platform_ocr_available(host))
    )
    if available():
        return
    if ocr_platform_id(host) == "linux":
        from src.integrations.receipt_ocr.tesseract_ocr import (
            tesseract_bindings_importable,
            tesseract_engine_found,
        )

        if tesseract_bindings_importable() and not tesseract_engine_found():
            raise ReceiptOcrInstallError(_TESSERACT_ENGINE_MISSING)
    raise ReceiptOcrInstallError(_STILL_UNAVAILABLE)


def _platform_ocr_available(platform: str) -> bool:
    kind = ocr_platform_id(platform)
    if kind == "macos":
        from src.integrations.receipt_ocr.macos_vision import macos_vision_is_available

        return macos_vision_is_available()
    if kind == "windows":
        from src.integrations.receipt_ocr.windows_ocr import windows_ocr_is_available

        return windows_ocr_is_available()
    if kind == "linux":
        from src.integrations.receipt_ocr.tesseract_ocr import tesseract_ocr_is_available

        return tesseract_ocr_is_available()
    return False


def _pip_failure_detail(result: CompletedProcess[str]) -> str:
    combined = (result.stderr or result.stdout or "").strip()
    if not combined:
        return "pip failed"
    last_line = combined.splitlines()[-1].strip()
    if len(last_line) > 200:
        return last_line[-200:]
    return last_line or "pip failed"
