from __future__ import annotations

import sys
from pathlib import Path

from src.domain.exceptions import ReceiptOcrUnavailableError
from src.domain.receipt_ocr import ReceiptOcrResult

PROVIDER_ID = "unsupported"


class UnsupportedReceiptOcrProvider:
    """No-op OCR backend for platforms without a Tier A implementation."""

    def __init__(self, platform: str | None = None) -> None:
        self._platform = platform if platform is not None else sys.platform

    @property
    def provider_id(self) -> str:
        return PROVIDER_ID

    def extract_text(self, image_path: Path) -> ReceiptOcrResult:
        _ = image_path
        msg = (
            "Receipt scanning is not available on this platform "
            f"({self._platform}). Enter the expense manually."
        )
        raise ReceiptOcrUnavailableError(msg)
