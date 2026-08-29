from __future__ import annotations

import sys

from src.domain.receipt_ocr import ReceiptOcrProvider
from src.integrations.receipt_ocr.macos_vision import (
    MacosVisionOcrProvider,
    macos_vision_is_available,
)
from src.integrations.receipt_ocr.unsupported import UnsupportedReceiptOcrProvider


def create_receipt_ocr_provider() -> ReceiptOcrProvider:
    """Return the best available on-device OCR provider for this host OS."""
    if sys.platform == "darwin":
        return MacosVisionOcrProvider()
    return UnsupportedReceiptOcrProvider()


def receipt_ocr_is_available() -> bool:
    """True when on-device OCR can run (macOS Vision + PyObjC)."""
    return sys.platform == "darwin" and macos_vision_is_available()
