from __future__ import annotations

from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReceiptOcrLine(BaseModel):
    """Single OCR text line with a provider-reported confidence score."""

    model_config = ConfigDict(frozen=True)

    text: str
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("text")
    @classmethod
    def _strip_text(cls, value: str) -> str:
        return value.strip()


class ReceiptOcrResult(BaseModel):
    """Structured OCR output for receipt field parsing and review UI."""

    model_config = ConfigDict(frozen=True)

    lines: tuple[ReceiptOcrLine, ...]
    provider_id: str
    overall_confidence: float = Field(ge=0.0, le=1.0)

    @property
    def full_text(self) -> str:
        return "\n".join(line.text for line in self.lines if line.text)


class ReceiptOcrProvider(Protocol):
    """Platform OCR backend used by receipt-assisted expense entry (Story 33)."""

    @property
    def provider_id(self) -> str:
        """Stable identifier for logging, Settings copy, and test doubles."""
        ...

    def extract_text(self, image_path: Path) -> ReceiptOcrResult:
        """Run OCR on a receipt image stored on disk.

        Implementations must not mutate application data. They may raise
        ``ReceiptOcrUnavailableError`` when OCR is unsupported on the host OS
        or ``ReceiptOcrError`` when the image cannot be read or processed.
        """
        ...
