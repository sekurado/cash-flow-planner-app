from __future__ import annotations

import shutil
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from src.domain.exceptions import ReceiptOcrError, ReceiptOcrUnavailableError
from src.domain.receipt_ocr import ReceiptOcrLine, ReceiptOcrResult

PROVIDER_ID = "tesseract"

RecognizeLines = Callable[[Path], Sequence[tuple[str, float]]]


class TesseractOcrProvider:
    """On-device OCR via Tesseract (Linux best-effort Tier A)."""

    def __init__(self, recognize: RecognizeLines | None = None) -> None:
        self._recognize = recognize or _recognize_with_tesseract

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


def tesseract_bindings_importable() -> bool:
    try:
        _import_tesseract()
    except ReceiptOcrUnavailableError:
        return False
    return True


def tesseract_engine_found() -> bool:
    return shutil.which("tesseract") is not None


def tesseract_ocr_is_available() -> bool:
    return tesseract_bindings_importable() and tesseract_engine_found()


def _recognize_with_tesseract(image_path: Path) -> Sequence[tuple[str, float]]:
    if not tesseract_engine_found():
        msg = (
            "The Tesseract OCR engine was not found. Install it with your package "
            "manager (for example: apt install tesseract-ocr) and try again, "
            "or enter the expense manually."
        )
        raise ReceiptOcrUnavailableError(msg)
    pytesseract, image_mod = _import_tesseract()
    with image_mod.open(str(image_path.resolve())) as image:
        output_type = getattr(getattr(pytesseract, "Output", None), "DICT", "dict")
        data = pytesseract.image_to_data(image, output_type=output_type)
    if not isinstance(data, Mapping):
        msg = "Could not read text from receipt image: unexpected Tesseract output"
        raise ReceiptOcrError(msg)
    return _lines_from_tesseract_data(data)


def _lines_from_tesseract_data(
    data: Mapping[str, Sequence[object]],
) -> tuple[tuple[str, float], ...]:
    texts = data.get("text", ())
    confs = data.get("conf", ())
    blocks = data.get("block_num", ())
    pars = data.get("par_num", ())
    line_nums = data.get("line_num", ())
    grouped: dict[tuple[int, int, int], list[tuple[str, float]]] = {}
    for index, raw_text in enumerate(texts):
        text = str(raw_text).strip()
        if not text:
            continue
        conf_raw = _as_float(confs[index] if index < len(confs) else 0.0)
        confidence = 0.0 if conf_raw < 0 else min(1.0, conf_raw / 100.0)
        key = (
            _as_int(blocks[index] if index < len(blocks) else 0),
            _as_int(pars[index] if index < len(pars) else 0),
            _as_int(line_nums[index] if index < len(line_nums) else index),
        )
        grouped.setdefault(key, []).append((text, confidence))
    lines: list[tuple[str, float]] = []
    for key in sorted(grouped):
        words = grouped[key]
        joined = " ".join(word for word, _confidence in words)
        mean = sum(confidence for _word, confidence in words) / len(words)
        lines.append((joined, mean))
    return tuple(lines)


def _import_tesseract() -> tuple[Any, Any]:
    try:
        import pytesseract  # type: ignore[import-not-found]
        from PIL import Image
    except ImportError as exc:
        msg = (
            "Receipt OCR on Linux requires Tesseract Python bindings. "
            "Install on-device scanning from Settings, or enter the expense manually."
        )
        raise ReceiptOcrUnavailableError(msg) from exc
    return pytesseract, Image


def _as_int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return 0
    return 0


def _as_float(value: object) -> float:
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, value))


def _mean_confidence(lines: Sequence[ReceiptOcrLine]) -> float:
    if not lines:
        return 0.0
    return sum(line.confidence for line in lines) / len(lines)
