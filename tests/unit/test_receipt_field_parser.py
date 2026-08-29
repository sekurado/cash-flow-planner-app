from __future__ import annotations

from datetime import date

import pytest

from src.domain.receipt_field_parser import (
    LOW_CONFIDENCE_THRESHOLD,
    ReceiptFieldParser,
)
from src.domain.receipt_ocr import ReceiptOcrLine, ReceiptOcrResult

_REFERENCE = date(2026, 8, 29)

CAFE_NERO = """\
CAFE NERO
123 High Street
London
Date: 12/05/2024
Latte          4.50
Muffin         3.20
Subtotal       7.70
Tax            0.80
TOTAL         12.50
Thank you
"""

GROCERY_EUROPEAN = """\
BIO MARKT
www.biomarkt.example
Tel +49 30 1234567
12.03.2026
Milch  1,99
Brot   2,49
Zwischensumme  4,48
MwSt   0,52
SUMME TOTAL    4,48
"""

NO_TOTAL_KEYWORD = """\
Corner Shop
Coffee  3.50
Pastry  2.75
"""

AMOUNT_DUE_RECEIPT = """\
City Garage
Invoice 4412
AMOUNT DUE  186.00
Paid 01.02.2026
"""


def _result_from_blob(blob: str, *, confidence: float = 1.0) -> ReceiptOcrResult:
    lines = tuple(
        ReceiptOcrLine(text=line, confidence=confidence)
        for line in blob.splitlines()
        if line.strip()
    )
    return ReceiptOcrResult(
        lines=lines,
        provider_id="fixture",
        overall_confidence=confidence,
    )


def _parse(blob: str, *, dayfirst: bool = True) -> ReceiptFieldParser:
    return ReceiptFieldParser(reference_date=_REFERENCE, dayfirst=dayfirst)


@pytest.mark.unit
def test_parser_reads_total_keyword_and_skips_subtotal_tax() -> None:
    hints = _parse(CAFE_NERO).parse(_result_from_blob(CAFE_NERO))

    assert hints.amount == pytest.approx(12.50)
    assert hints.amount_source is not None
    assert "TOTAL" in hints.amount_source
    assert hints.amount_confidence >= LOW_CONFIDENCE_THRESHOLD
    assert not hints.amount_is_low_confidence


@pytest.mark.unit
def test_parser_reads_european_decimal_comma_and_dot_date() -> None:
    hints = _parse(GROCERY_EUROPEAN).parse(_result_from_blob(GROCERY_EUROPEAN))

    assert hints.amount == pytest.approx(4.48)
    assert hints.occurred_on == date(2026, 3, 12)
    assert hints.merchant == "BIO MARKT"


@pytest.mark.unit
def test_parser_falls_back_to_largest_amount_without_total_keyword() -> None:
    hints = _parse(NO_TOTAL_KEYWORD).parse(_result_from_blob(NO_TOTAL_KEYWORD))

    assert hints.amount == pytest.approx(3.50)
    assert hints.amount_is_low_confidence
    assert hints.merchant == "Corner Shop"


@pytest.mark.unit
def test_parser_reads_amount_due() -> None:
    hints = _parse(AMOUNT_DUE_RECEIPT).parse(_result_from_blob(AMOUNT_DUE_RECEIPT))

    assert hints.amount == pytest.approx(186.0)
    assert hints.occurred_on == date(2026, 2, 1)
    assert hints.merchant == "City Garage"


@pytest.mark.unit
def test_parser_reads_iso_date() -> None:
    blob = "Cafe\n2025-11-03\nTOTAL 9.00\n"
    hints = _parse(blob).parse(_result_from_blob(blob))

    assert hints.occurred_on == date(2025, 11, 3)
    assert hints.amount == pytest.approx(9.0)


@pytest.mark.unit
def test_parser_slash_date_uses_dayfirst_when_ambiguous() -> None:
    blob = "Shop\nDate: 05/06/2025\nTOTAL 1.00\n"
    dayfirst = _parse(blob, dayfirst=True).parse(_result_from_blob(blob))
    monthfirst = _parse(blob, dayfirst=False).parse(_result_from_blob(blob))

    assert dayfirst.occurred_on == date(2025, 6, 5)
    assert monthfirst.occurred_on == date(2025, 5, 6)


@pytest.mark.unit
def test_parser_reads_month_name_date() -> None:
    blob = "Bakery\nMay 12, 2025\nTOTAL 8.00\n"
    hints = _parse(blob).parse(_result_from_blob(blob))

    assert hints.occurred_on == date(2025, 5, 12)


@pytest.mark.unit
def test_parser_does_not_treat_year_as_amount() -> None:
    blob = "Store\n2024\nCoffee 4.00\n"
    hints = _parse(blob).parse(_result_from_blob(blob))

    assert hints.amount == pytest.approx(4.00)


@pytest.mark.unit
def test_parser_prefers_last_total_line() -> None:
    blob = "Cafe\nTOTAL 3.00\nTOTAL 11.25\n"
    hints = _parse(blob).parse(_result_from_blob(blob))

    assert hints.amount == pytest.approx(11.25)


@pytest.mark.unit
def test_parser_skips_url_phone_and_street_for_merchant() -> None:
    blob = """\
www.example.com
Tel +1 555 0100
10 Main Street
Green Grocer
TOTAL 6.00
"""
    hints = _parse(blob).parse(_result_from_blob(blob))

    assert hints.merchant == "Green Grocer"
    assert hints.merchant_is_low_confidence


@pytest.mark.unit
def test_parser_empty_ocr_returns_empty_suggestions() -> None:
    empty = ReceiptOcrResult(lines=(), provider_id="fixture", overall_confidence=0.0)
    hints = ReceiptFieldParser(reference_date=_REFERENCE).parse(empty)

    assert hints.amount is None
    assert hints.occurred_on is None
    assert hints.merchant is None
    assert hints.amount_is_low_confidence
    assert hints.date_is_low_confidence
    assert hints.merchant_is_low_confidence


@pytest.mark.unit
def test_parser_rejects_future_dates() -> None:
    blob = "Shop\n01.01.2099\nTOTAL 2.00\n"
    hints = _parse(blob).parse(_result_from_blob(blob))

    assert hints.occurred_on is None
    assert hints.amount == pytest.approx(2.00)


@pytest.mark.unit
def test_parser_reads_thousands_separator() -> None:
    blob = "Dealer\nTOTAL 1,234.56\n"
    hints = _parse(blob).parse(_result_from_blob(blob))

    assert hints.amount == pytest.approx(1234.56)
