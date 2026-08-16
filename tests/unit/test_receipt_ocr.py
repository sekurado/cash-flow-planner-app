from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from src.domain.receipt_ocr import ReceiptOcrLine, ReceiptOcrResult


@pytest.mark.unit
def test_receipt_ocr_line_strips_text_and_validates_confidence() -> None:
    line = ReceiptOcrLine(text="  Coffee  ", confidence=0.85)

    assert line.text == "Coffee"
    assert line.confidence == pytest.approx(0.85)


@pytest.mark.unit
def test_receipt_ocr_line_rejects_confidence_outside_unit_interval() -> None:
    with pytest.raises(ValidationError):
        ReceiptOcrLine(text="Total", confidence=1.5)


@pytest.mark.unit
def test_receipt_ocr_result_full_text_joins_non_empty_lines() -> None:
    result = ReceiptOcrResult(
        lines=(
            ReceiptOcrLine(text="Cafe Nero", confidence=0.9),
            ReceiptOcrLine(text="TOTAL 12.50", confidence=0.8),
        ),
        provider_id="test-provider",
        overall_confidence=0.85,
    )

    assert result.full_text == "Cafe Nero\nTOTAL 12.50"
    assert result.provider_id == "test-provider"


@pytest.mark.unit
def test_receipt_ocr_provider_protocol_is_structurally_implemented() -> None:
    class StubProvider:
        @property
        def provider_id(self) -> str:
            return "stub"

        def extract_text(self, image_path: Path) -> ReceiptOcrResult:
            _ = image_path
            return ReceiptOcrResult(
                lines=(ReceiptOcrLine(text="TOTAL 10.00", confidence=0.7),),
                provider_id=self.provider_id,
                overall_confidence=0.7,
            )

    provider = StubProvider()
    result = provider.extract_text(Path("/tmp/receipt.jpg"))

    assert result.lines[0].text == "TOTAL 10.00"
