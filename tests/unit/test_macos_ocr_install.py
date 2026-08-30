from __future__ import annotations

from collections.abc import Sequence
from subprocess import CompletedProcess, TimeoutExpired

import pytest

from src.integrations.receipt_ocr.macos_ocr_install import (
    MACOS_OCR_PACKAGES,
    MacosOcrInstallError,
    can_install_macos_ocr,
    install_macos_ocr_bindings,
)


@pytest.mark.unit
def test_can_install_macos_ocr_only_on_source_darwin() -> None:
    assert can_install_macos_ocr(platform="darwin", frozen=False) is True
    assert can_install_macos_ocr(platform="darwin", frozen=True) is False
    assert can_install_macos_ocr(platform="linux", frozen=False) is False
    assert can_install_macos_ocr(platform="win32", frozen=False) is False


@pytest.mark.unit
def test_install_rejects_non_macos() -> None:
    with pytest.raises(MacosOcrInstallError, match="only be installed on macOS"):
        install_macos_ocr_bindings(platform="linux", frozen=False)


@pytest.mark.unit
def test_install_rejects_frozen_app() -> None:
    with pytest.raises(MacosOcrInstallError, match="this app build"):
        install_macos_ocr_bindings(platform="darwin", frozen=True)


@pytest.mark.unit
def test_install_runs_pip_and_verifies_vision() -> None:
    recorded: list[list[str]] = []

    def fake_run(
        args: Sequence[str],
        **kwargs: object,
    ) -> CompletedProcess[str]:
        _ = kwargs
        recorded.append(list(args))
        return CompletedProcess(args=list(args), returncode=0, stdout="ok", stderr="")

    install_macos_ocr_bindings(
        platform="darwin",
        frozen=False,
        python_executable="/venv/bin/python",
        run=fake_run,
        vision_available=lambda: True,
    )

    assert recorded == [["/venv/bin/python", "-m", "pip", "install", *MACOS_OCR_PACKAGES]]


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

    with pytest.raises(MacosOcrInstallError, match="Could not install"):
        install_macos_ocr_bindings(
            platform="darwin",
            frozen=False,
            run=fake_run,
            vision_available=lambda: False,
        )


@pytest.mark.unit
def test_install_raises_on_timeout() -> None:
    def fake_run(args: Sequence[str], **kwargs: object) -> CompletedProcess[str]:
        _ = kwargs
        raise TimeoutExpired(cmd=list(args), timeout=1)

    with pytest.raises(MacosOcrInstallError, match="timed out"):
        install_macos_ocr_bindings(
            platform="darwin",
            frozen=False,
            run=fake_run,
            vision_available=lambda: False,
        )


@pytest.mark.unit
def test_install_raises_when_vision_still_missing() -> None:
    def fake_run(args: Sequence[str], **kwargs: object) -> CompletedProcess[str]:
        _ = kwargs
        return CompletedProcess(args=list(args), returncode=0, stdout="ok", stderr="")

    with pytest.raises(MacosOcrInstallError, match="Restart the app"):
        install_macos_ocr_bindings(
            platform="darwin",
            frozen=False,
            run=fake_run,
            vision_available=lambda: False,
        )
