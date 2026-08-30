from __future__ import annotations

import importlib
import sys
from collections.abc import Callable, Sequence
from subprocess import CompletedProcess, TimeoutExpired
from subprocess import run as subprocess_run

from src.integrations.receipt_ocr.macos_vision import macos_vision_is_available

MACOS_OCR_PACKAGES: tuple[str, ...] = (
    "pyobjc-framework-Vision",
    "pyobjc-framework-Cocoa",
)
_INSTALL_TIMEOUT_SECONDS = 180


class MacosOcrInstallError(OSError):
    """Raised when macOS Vision OCR bindings cannot be installed."""


def is_frozen_runtime() -> bool:
    return bool(getattr(sys, "frozen", False))


def can_install_macos_ocr(*, platform: str | None = None, frozen: bool | None = None) -> bool:
    """True when pip can add Vision bindings to this interpreter (source run on macOS)."""
    host = sys.platform if platform is None else platform
    is_frozen = is_frozen_runtime() if frozen is None else frozen
    return host == "darwin" and not is_frozen


def install_macos_ocr_bindings(
    *,
    platform: str | None = None,
    frozen: bool | None = None,
    python_executable: str | None = None,
    run: Callable[..., CompletedProcess[str]] | None = None,
    vision_available: Callable[[], bool] | None = None,
) -> None:
    """Install PyObjC Vision bindings into the running interpreter."""
    if not can_install_macos_ocr(platform=platform, frozen=frozen):
        host = sys.platform if platform is None else platform
        if host != "darwin":
            msg = "On-device receipt scanning can only be installed on macOS."
            raise MacosOcrInstallError(msg)
        msg = "On-device receipt scanning cannot be installed in this app build."
        raise MacosOcrInstallError(msg)

    python = python_executable if python_executable is not None else sys.executable
    runner = run if run is not None else subprocess_run
    args: Sequence[str] = (
        python,
        "-m",
        "pip",
        "install",
        *MACOS_OCR_PACKAGES,
    )
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
        raise MacosOcrInstallError(msg) from exc
    except TimeoutExpired as exc:
        msg = "Installing on-device receipt scanning timed out. Check your network and try again."
        raise MacosOcrInstallError(msg) from exc

    if result.returncode != 0:
        detail = _pip_failure_detail(result)
        msg = f"Could not install on-device receipt scanning: {detail}"
        raise MacosOcrInstallError(msg)

    importlib.invalidate_caches()
    available = vision_available if vision_available is not None else macos_vision_is_available
    if not available():
        msg = (
            "Installed OCR packages but Vision is still unavailable. "
            "Restart the app and try Scan again."
        )
        raise MacosOcrInstallError(msg)


def _pip_failure_detail(result: CompletedProcess[str]) -> str:
    combined = (result.stderr or result.stdout or "").strip()
    if not combined:
        return "pip failed"
    last_line = combined.splitlines()[-1].strip()
    if len(last_line) > 200:
        return last_line[-200:]
    return last_line or "pip failed"
