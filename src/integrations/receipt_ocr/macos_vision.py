from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from src.domain.exceptions import ReceiptOcrError, ReceiptOcrUnavailableError
from src.domain.receipt_ocr import ReceiptOcrLine, ReceiptOcrResult

PROVIDER_ID = "vision-macos"

RecognizeLines = Callable[[Path], Sequence[tuple[str, float]]]


class MacosVisionOcrProvider:
    """On-device OCR via the macOS Vision framework (Tier A)."""

    def __init__(self, recognize: RecognizeLines | None = None) -> None:
        self._recognize = recognize or _recognize_with_vision

    @property
    def provider_id(self) -> str:
        return PROVIDER_ID

    def extract_text(self, image_path: Path) -> ReceiptOcrResult:
        path = image_path.expanduser()
        if not path.is_file():
            msg = f"Receipt image not found: {path}"
            raise ReceiptOcrError(msg)
        raw_lines = self._recognize(path)
        lines = tuple(
            ReceiptOcrLine(text=text, confidence=_clamp_unit(confidence))
            for text, confidence in raw_lines
            if text.strip()
        )
        return ReceiptOcrResult(
            lines=lines,
            provider_id=self.provider_id,
            overall_confidence=_mean_confidence(lines),
        )


def macos_vision_is_available() -> bool:
    try:
        _import_macos_vision()
    except ReceiptOcrUnavailableError:
        return False
    return True


def _recognize_with_vision(image_path: Path) -> Sequence[tuple[str, float]]:
    vision, nsurl = _import_macos_vision()
    url = nsurl.fileURLWithPath_(str(image_path.resolve()))
    request = vision.VNRecognizeTextRequest.alloc().init()
    accurate = getattr(vision, "VNRequestTextRecognitionLevelAccurate", 0)
    set_level = getattr(request, "setRecognitionLevel_", None)
    if callable(set_level):
        set_level(accurate)
    set_language = getattr(request, "setAutomaticallyDetectsLanguage_", None)
    if callable(set_language):
        set_language(True)
    set_correction = getattr(request, "setUsesLanguageCorrection_", None)
    if callable(set_correction):
        set_correction(True)

    handler = vision.VNImageRequestHandler.alloc().initWithURL_options_(url, None)
    outcome = handler.performRequests_error_([request], None)
    success, error = _unpack_objc_outcome(outcome)
    if not success:
        detail = str(error) if error is not None else "Vision request failed"
        msg = f"Could not read text from receipt image: {detail}"
        raise ReceiptOcrError(msg)

    observations = request.results()
    if observations is None:
        return ()
    lines: list[tuple[str, float]] = []
    for observation in observations:
        candidates = observation.topCandidates_(1)
        if not candidates:
            continue
        candidate = candidates[0]
        text = str(candidate.string())
        confidence = float(candidate.confidence())
        if text.strip():
            lines.append((text, confidence))
    return tuple(lines)


def _import_macos_vision() -> tuple[Any, Any]:
    try:
        import Vision  # type: ignore[import-not-found]
        from Foundation import NSURL  # type: ignore[import-not-found]
    except ImportError as exc:
        msg = (
            "Receipt OCR on macOS requires PyObjC Vision bindings. "
            "Install on-device scanning from Settings, or enter the expense manually."
        )
        raise ReceiptOcrUnavailableError(msg) from exc
    return Vision, NSURL


def _unpack_objc_outcome(outcome: object) -> tuple[bool, object | None]:
    if isinstance(outcome, tuple):
        if not outcome:
            return False, None
        success = bool(outcome[0])
        error = outcome[1] if len(outcome) > 1 else None
        return success, error
    return bool(outcome), None


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, value))


def _mean_confidence(lines: Sequence[ReceiptOcrLine]) -> float:
    if not lines:
        return 0.0
    return sum(line.confidence for line in lines) / len(lines)
