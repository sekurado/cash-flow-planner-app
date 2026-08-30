from __future__ import annotations

import sys

from src.domain.receipt_ocr import ReceiptOcrProvider
from src.integrations.receipt_ocr.macos_vision import (
    MacosVisionOcrProvider,
    macos_vision_is_available,
)
from src.integrations.receipt_ocr.tesseract_ocr import (
    TesseractOcrProvider,
    tesseract_ocr_is_available,
)
from src.integrations.receipt_ocr.unsupported import UnsupportedReceiptOcrProvider
from src.integrations.receipt_ocr.windows_ocr import (
    WindowsOcrProvider,
    windows_ocr_is_available,
)


def create_receipt_ocr_provider() -> ReceiptOcrProvider:
    """Return the best available on-device OCR provider for this host OS."""
    if sys.platform == "darwin":
        return MacosVisionOcrProvider()
    if sys.platform == "win32":
        return WindowsOcrProvider()
    if sys.platform.startswith("linux"):
        return TesseractOcrProvider()
    return UnsupportedReceiptOcrProvider()


def receipt_ocr_is_available() -> bool:
    """True when on-device OCR can run on this host."""
    if sys.platform == "darwin":
        return macos_vision_is_available()
    if sys.platform == "win32":
        return windows_ocr_is_available()
    if sys.platform.startswith("linux"):
        return tesseract_ocr_is_available()
    return False
