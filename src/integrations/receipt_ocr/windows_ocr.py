from __future__ import annotations

import asyncio
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from src.domain.exceptions import ReceiptOcrError, ReceiptOcrUnavailableError
from src.domain.receipt_ocr import ReceiptOcrLine, ReceiptOcrResult

PROVIDER_ID = "winrt-ocr"
_DEFAULT_LINE_CONFIDENCE = 0.75

RecognizeLines = Callable[[Path], Sequence[tuple[str, float]]]


class WindowsOcrProvider:
    """On-device OCR via Windows.Media.Ocr (Tier A)."""

    def __init__(self, recognize: RecognizeLines | None = None) -> None:
        self._recognize = recognize or _recognize_with_winrt

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


def windows_ocr_is_available() -> bool:
    try:
        _import_windows_ocr()
    except ReceiptOcrUnavailableError:
        return False
    return True


def _recognize_with_winrt(image_path: Path) -> Sequence[tuple[str, float]]:
    return asyncio.run(_recognize_with_winrt_async(image_path))


async def _recognize_with_winrt_async(image_path: Path) -> Sequence[tuple[str, float]]:
    ocr_ns, imaging_ns, storage_ns = _import_windows_ocr()
    file = await storage_ns.StorageFile.get_file_from_path_async(str(image_path.resolve()))
    access = getattr(storage_ns.FileAccessMode, "READ", 0)
    stream = await file.open_async(access)
    decoder = await imaging_ns.BitmapDecoder.create_async(stream)
    bitmap = await decoder.get_software_bitmap_async()
    engine = ocr_ns.OcrEngine.try_create_from_user_profile_languages()
    if engine is None:
        msg = (
            "Windows OCR is not available. Install an OCR language pack in Windows "
            "Settings and try again, or enter the expense manually."
        )
        raise ReceiptOcrUnavailableError(msg)
    result = await engine.recognize_async(bitmap)
    ocr_lines = getattr(result, "lines", None)
    if ocr_lines is None:
        return ()
    lines: list[tuple[str, float]] = []
    for line in ocr_lines:
        text = str(getattr(line, "text", "")).strip()
        if text:
            lines.append((text, _DEFAULT_LINE_CONFIDENCE))
    return tuple(lines)


def _import_windows_ocr() -> tuple[Any, Any, Any]:
    try:
        from winrt.windows.graphics.imaging import BitmapDecoder  # type: ignore[import-not-found]
        from winrt.windows.media.ocr import OcrEngine  # type: ignore[import-not-found]
        from winrt.windows.storage import (  # type: ignore[import-not-found]
            FileAccessMode,
            StorageFile,
        )
    except ImportError as exc:
        msg = (
            "Receipt OCR on Windows requires WinRT OCR bindings. "
            "Install on-device scanning from Settings, or enter the expense manually."
        )
        raise ReceiptOcrUnavailableError(msg) from exc
    ocr_ns = type("OcrNs", (), {"OcrEngine": OcrEngine})
    imaging_ns = type("ImagingNs", (), {"BitmapDecoder": BitmapDecoder})
    storage_ns = type(
        "StorageNs",
        (),
        {"StorageFile": StorageFile, "FileAccessMode": FileAccessMode},
    )
    return ocr_ns, imaging_ns, storage_ns


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, value))


def _mean_confidence(lines: Sequence[ReceiptOcrLine]) -> float:
    if not lines:
        return 0.0
    return sum(line.confidence for line in lines) / len(lines)
