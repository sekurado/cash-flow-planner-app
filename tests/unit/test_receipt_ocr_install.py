from __future__ import annotations

from collections.abc import Sequence
from subprocess import CompletedProcess, TimeoutExpired

import pytest

from src.integrations.receipt_ocr.receipt_ocr_install import (
    LINUX_OCR_PACKAGES,
    MACOS_OCR_PACKAGES,
    WINDOWS_OCR_PACKAGES,
    ReceiptOcrInstallError,
    can_install_receipt_ocr,
    install_receipt_ocr_bindings,
    ocr_platform_id,
)


@pytest.mark.unit
def test_ocr_platform_id() -> None:
    assert ocr_platform_id("darwin") == "macos"
    assert ocr_platform_id("win32") == "windows"
    assert ocr_platform_id("linux") == "linux"
    assert ocr_platform_id("freebsd14") == "other"


@pytest.mark.unit
def test_can_install_receipt_ocr_on_source_desktop_os() -> None:
    assert can_install_receipt_ocr(platform="darwin", frozen=False) is True
    assert can_install_receipt_ocr(platform="win32", frozen=False) is True
    assert can_install_receipt_ocr(platform="linux", frozen=False) is True
    assert can_install_receipt_ocr(platform="darwin", frozen=True) is False
    assert can_install_receipt_ocr(platform="win32", frozen=True) is False
    assert can_install_receipt_ocr(platform="aix", frozen=False) is False


@pytest.mark.unit
def test_install_rejects_unsupported_platform() -> None:
    with pytest.raises(ReceiptOcrInstallError, match="not available on this platform"):
        install_receipt_ocr_bindings(platform="aix", frozen=False)


@pytest.mark.unit
def test_install_rejects_frozen_app() -> None:
    with pytest.raises(ReceiptOcrInstallError, match="this app build"):
        install_receipt_ocr_bindings(platform="linux", frozen=True)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("platform", "packages"),
    [
        ("darwin", MACOS_OCR_PACKAGES),
        ("win32", WINDOWS_OCR_PACKAGES),
        ("linux", LINUX_OCR_PACKAGES),
    ],
)
def test_install_runs_pip_for_platform(
    platform: str,
    packages: tuple[str, ...],
) -> None:
    recorded: list[list[str]] = []

    def fake_run(args: Sequence[str], **kwargs: object) -> CompletedProcess[str]:
        _ = kwargs
        recorded.append(list(args))
        return CompletedProcess(args=list(args), returncode=0, stdout="ok", stderr="")

    install_receipt_ocr_bindings(
        platform=platform,
        frozen=False,
        python_executable="/venv/bin/python",
        run=fake_run,
        ocr_available=lambda: True,
    )

    assert recorded == [["/venv/bin/python", "-m", "pip", "install", *packages]]


@pytest.mark.unit
def test_install_raises_when_pip_fails() -> None:
    def fake_run(args: Sequence[str], **kwargs: object) -> CompletedProcess[str]:
        _ = kwargs
        return CompletedProcess(
            args=list(args),
            returncode=1,
            stdout="",
            stderr="ERROR: Could not find a version that satisfies the requirement\n",
        )

    with pytest.raises(ReceiptOcrInstallError, match="Could not install"):
        install_receipt_ocr_bindings(
            platform="win32",
            frozen=False,
            run=fake_run,
            ocr_available=lambda: False,
        )


@pytest.mark.unit
def test_install_raises_on_timeout() -> None:
    def fake_run(args: Sequence[str], **kwargs: object) -> CompletedProcess[str]:
        _ = kwargs
        raise TimeoutExpired(cmd=list(args), timeout=1)

    with pytest.raises(ReceiptOcrInstallError, match="timed out"):
        install_receipt_ocr_bindings(
            platform="darwin",
            frozen=False,
            run=fake_run,
            ocr_available=lambda: False,
        )


@pytest.mark.unit
def test_install_raises_when_still_unavailable() -> None:
    def fake_run(args: Sequence[str], **kwargs: object) -> CompletedProcess[str]:
        _ = kwargs
        return CompletedProcess(args=list(args), returncode=0, stdout="ok", stderr="")

    with pytest.raises(ReceiptOcrInstallError, match="still unavailable"):
        install_receipt_ocr_bindings(
            platform="darwin",
            frozen=False,
            run=fake_run,
            ocr_available=lambda: False,
        )


@pytest.mark.unit
def test_install_linux_reports_missing_tesseract_engine(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(args: Sequence[str], **kwargs: object) -> CompletedProcess[str]:
        _ = kwargs
        return CompletedProcess(args=list(args), returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(
        "src.integrations.receipt_ocr.tesseract_ocr.tesseract_bindings_importable",
        lambda: True,
    )
    monkeypatch.setattr(
        "src.integrations.receipt_ocr.tesseract_ocr.tesseract_engine_found",
        lambda: False,
    )

    with pytest.raises(ReceiptOcrInstallError, match="Tesseract engine was not found"):
        install_receipt_ocr_bindings(
            platform="linux",
            frozen=False,
            run=fake_run,
            ocr_available=lambda: False,
        )
