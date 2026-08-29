from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.domain.exceptions import ReceiptOcrError, ReceiptOcrUnavailableError
from src.integrations.receipt_ocr import (
    create_receipt_ocr_provider,
    receipt_ocr_is_available,
)
from src.integrations.receipt_ocr.macos_vision import (
    MacosVisionOcrProvider,
    _import_macos_vision,
    _recognize_with_vision,
)
from src.integrations.receipt_ocr.unsupported import UnsupportedReceiptOcrProvider


@pytest.mark.unit
def test_unsupported_provider_raises_unavailable(tmp_path: Path) -> None:
    provider = UnsupportedReceiptOcrProvider(platform="linux")
    image = tmp_path / "receipt.jpg"
    image.write_bytes(b"not-an-image")

    with pytest.raises(ReceiptOcrUnavailableError, match="linux"):
        provider.extract_text(image)
    assert provider.provider_id == "unsupported"


@pytest.mark.unit
def test_macos_provider_uses_injected_recognizer(tmp_path: Path) -> None:
    image = tmp_path / "receipt.png"
    image.write_bytes(b"fake")

    def recognize(path: Path) -> Sequence[tuple[str, float]]:
        assert path == image
        return (("Cafe Nero", 0.9), ("TOTAL 12.50", 0.8))

    provider = MacosVisionOcrProvider(recognize=recognize)
    result = provider.extract_text(image)

    assert result.provider_id == "vision-macos"
    assert result.lines[0].text == "Cafe Nero"
    assert result.lines[1].text == "TOTAL 12.50"
    assert result.overall_confidence == pytest.approx(0.85)


@pytest.mark.unit
def test_macos_provider_missing_file_raises_ocr_error(tmp_path: Path) -> None:
    provider = MacosVisionOcrProvider(recognize=lambda path: ())
    missing = tmp_path / "missing.jpg"

    with pytest.raises(ReceiptOcrError, match="not found"):
        provider.extract_text(missing)


@pytest.mark.unit
def test_macos_provider_empty_ocr_has_zero_confidence(tmp_path: Path) -> None:
    image = tmp_path / "blank.png"
    image.write_bytes(b"x")
    provider = MacosVisionOcrProvider(recognize=lambda path: ())

    result = provider.extract_text(image)

    assert result.lines == ()
    assert result.overall_confidence == pytest.approx(0.0)


@pytest.mark.unit
def test_factory_returns_macos_provider_on_darwin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.integrations.receipt_ocr.sys.platform", "darwin")

    provider = create_receipt_ocr_provider()

    assert isinstance(provider, MacosVisionOcrProvider)


@pytest.mark.unit
def test_factory_returns_unsupported_on_other_os(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.integrations.receipt_ocr.sys.platform", "win32")

    provider = create_receipt_ocr_provider()

    assert isinstance(provider, UnsupportedReceiptOcrProvider)


@pytest.mark.unit
def test_receipt_ocr_is_available_false_off_macos(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.integrations.receipt_ocr.sys.platform", "linux")

    assert receipt_ocr_is_available() is False


class _FakeCandidate:
    def string(self) -> str:
        return "TOTAL 10.00"

    def confidence(self) -> float:
        return 0.77


class _FakeObservation:
    def topCandidates_(self, count: int) -> list[_FakeCandidate]:
        assert count == 1
        return [_FakeCandidate()]


class _FakeRequest:
    def setRecognitionLevel_(self, level: int) -> None:
        _ = level

    def setAutomaticallyDetectsLanguage_(self, enabled: bool) -> None:
        _ = enabled

    def setUsesLanguageCorrection_(self, enabled: bool) -> None:
        _ = enabled

    def results(self) -> list[_FakeObservation]:
        return [_FakeObservation()]


class _FakeHandler:
    def __init__(self, *, success: bool = True) -> None:
        self._success = success

    def performRequests_error_(self, requests: object, error: object) -> bool:
        _ = requests, error
        return self._success


def _install_fake_vision(
    monkeypatch: pytest.MonkeyPatch,
    *,
    success: bool = True,
) -> None:
    fake_vision = SimpleNamespace(
        VNRecognizeTextRequest=SimpleNamespace(
            alloc=lambda: SimpleNamespace(init=_FakeRequest),
        ),
        VNImageRequestHandler=SimpleNamespace(
            alloc=lambda: SimpleNamespace(
                initWithURL_options_=lambda url, options: _FakeHandler(success=success),
            ),
        ),
        VNRequestTextRecognitionLevelAccurate=1,
    )
    fake_nsurl = SimpleNamespace(fileURLWithPath_=lambda path: f"file://{path}")
    monkeypatch.setattr(
        "src.integrations.receipt_ocr.macos_vision._import_macos_vision",
        lambda: (fake_vision, fake_nsurl),
    )


@pytest.mark.unit
def test_recognize_with_vision_uses_fake_runtime(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    image = tmp_path / "receipt.jpg"
    image.write_bytes(b"x")
    _install_fake_vision(monkeypatch)

    lines = _recognize_with_vision(image)

    assert lines == (("TOTAL 10.00", 0.77),)


@pytest.mark.unit
def test_recognize_with_vision_failed_request_raises(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    image = tmp_path / "receipt.jpg"
    image.write_bytes(b"x")
    _install_fake_vision(monkeypatch, success=False)

    with pytest.raises(ReceiptOcrError, match="Could not read text"):
        _recognize_with_vision(image)


@pytest.mark.unit
def test_import_macos_vision_missing_pyobjc(monkeypatch: pytest.MonkeyPatch) -> None:
    import builtins

    real_import = builtins.__import__

    def fake_import(name: str, *args: object, **kwargs: object) -> object:
        if name in {"Vision", "Foundation"}:
            raise ImportError("no pyobjc")
        return real_import(name, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(ReceiptOcrUnavailableError, match="PyObjC"):
        _import_macos_vision()
