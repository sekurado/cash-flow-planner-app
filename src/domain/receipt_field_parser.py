from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Final

from dateutil import parser as date_parser
from pydantic import BaseModel, ConfigDict, Field

from src.domain.receipt_ocr import ReceiptOcrLine, ReceiptOcrResult

LOW_CONFIDENCE_THRESHOLD: Final[float] = 0.6
_MAX_PAST_DAYS: Final[int] = 365 * 5
_MAX_FUTURE_DAYS: Final[int] = 1

_ISO_DATE_RE = re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b")
_DOT_DATE_RE = re.compile(r"\b(\d{1,2})\.(\d{1,2})\.(\d{2,4})\b")
_SLASH_DATE_RE = re.compile(r"\b(\d{1,2})([/-])(\d{1,2})([/-])(\d{2,4})\b")
_MONTH_NAME_DATE_RE = re.compile(
    r"\b(?:"
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|"
    r"dec(?:ember)?)\s+\d{1,2},?\s+\d{2,4}"
    r"|"
    r"\d{1,2}\s+(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
    r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|"
    r"nov(?:ember)?|dec(?:ember)?)\s+\d{2,4}"
    r")\b",
    re.IGNORECASE,
)
_MONEY_RE = re.compile(
    r"(?<!\d)(?:[$€£¥]\s*)?(\d{1,3}(?:[.,]\d{3})+|\d+)(?:([.,])(\d{1,2}))?(?!\d)"
)
_TOTAL_KEYWORD_RE = re.compile(
    r"\b(?:grand\s+total|amount\s+due|balance\s+due|total\s+due|"
    r"total\s+amount|amount\s+paid|total)\b",
    re.IGNORECASE,
)
_IGNORE_AMOUNT_RE = re.compile(
    r"\b(?:sub\s*total|tax|vat|gst|hst|pst|tip|gratuity|change|"
    r"cash|tender(?:ed)?)\b",
    re.IGNORECASE,
)
_DATE_KEYWORD_RE = re.compile(r"\b(?:date|dated|datetime)\b", re.IGNORECASE)
_PHONE_RE = re.compile(r"\+?\d[\d\s().-]{6,}\d")
_URL_RE = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)
_EMAIL_RE = re.compile(r"\S+@\S+\.\S+")
_STREET_RE = re.compile(
    r"^\d+\s+.+\b(?:st|street|ave|avenue|rd|road|blvd|lane|ln|dr|drive|"
    r"way|ct|court|pl|place)\b",
    re.IGNORECASE,
)
_POSTAL_RE = re.compile(
    r"\b(?:\d{5}(?:-\d{4})?|[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})\b",
    re.IGNORECASE,
)
_THANK_YOU_RE = re.compile(r"\bthank\s+you\b", re.IGNORECASE)


class ReceiptFieldHints(BaseModel):
    """Suggested expense fields extracted from OCR lines (always user-editable)."""

    model_config = ConfigDict(frozen=True)

    amount: float | None = None
    amount_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    amount_source: str | None = None
    occurred_on: date | None = None
    date_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    date_source: str | None = None
    merchant: str | None = None
    merchant_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    merchant_source: str | None = None

    @property
    def amount_is_low_confidence(self) -> bool:
        return self.amount is None or self.amount_confidence < LOW_CONFIDENCE_THRESHOLD

    @property
    def date_is_low_confidence(self) -> bool:
        return self.occurred_on is None or self.date_confidence < LOW_CONFIDENCE_THRESHOLD

    @property
    def merchant_is_low_confidence(self) -> bool:
        return self.merchant is None or self.merchant_confidence < LOW_CONFIDENCE_THRESHOLD


class ReceiptFieldParser:
    """Heuristic mapper from OCR lines to amount, date, and merchant hints."""

    def __init__(
        self,
        *,
        reference_date: date | None = None,
        dayfirst: bool = True,
    ) -> None:
        self._reference_date = reference_date
        self._dayfirst = dayfirst

    def parse(self, ocr_result: ReceiptOcrResult) -> ReceiptFieldHints:
        lines = tuple(line for line in ocr_result.lines if line.text)
        amount, amount_confidence, amount_source = self._suggest_amount(lines)
        occurred_on, date_confidence, date_source = self._suggest_date(lines)
        merchant, merchant_confidence, merchant_source = self._suggest_merchant(lines)
        return ReceiptFieldHints(
            amount=amount,
            amount_confidence=amount_confidence,
            amount_source=amount_source,
            occurred_on=occurred_on,
            date_confidence=date_confidence,
            date_source=date_source,
            merchant=merchant,
            merchant_confidence=merchant_confidence,
            merchant_source=merchant_source,
        )

    def _suggest_amount(
        self,
        lines: tuple[ReceiptOcrLine, ...],
    ) -> tuple[float | None, float, str | None]:
        keyword_hits: list[tuple[float, float, str]] = []
        fallback_hits: list[tuple[float, float, str]] = []
        for line in lines:
            amounts = _money_amounts(line.text)
            if not amounts:
                continue
            chosen = max(amounts)
            if _TOTAL_KEYWORD_RE.search(line.text) and not _is_subtotal_line(line.text):
                keyword_hits.append((chosen, line.confidence, line.text))
                continue
            if _IGNORE_AMOUNT_RE.search(line.text):
                continue
            fallback_hits.append((chosen, line.confidence, line.text))

        if keyword_hits:
            amount, ocr_confidence, source = keyword_hits[-1]
            return amount, _combined_confidence(0.9, ocr_confidence), source
        if fallback_hits:
            amount, ocr_confidence, source = max(fallback_hits, key=lambda item: item[0])
            return amount, _combined_confidence(0.55, ocr_confidence), source
        return None, 0.0, None

    def _suggest_date(
        self,
        lines: tuple[ReceiptOcrLine, ...],
    ) -> tuple[date | None, float, str | None]:
        reference = self._reference_date or date.today()
        keyword_hits: list[tuple[date, float, str]] = []
        other_hits: list[tuple[date, float, str]] = []
        for line in lines:
            parsed = self._dates_in_text(line.text, reference)
            if not parsed:
                continue
            chosen = parsed[-1]
            if _DATE_KEYWORD_RE.search(line.text):
                keyword_hits.append((chosen, line.confidence, line.text))
            else:
                other_hits.append((chosen, line.confidence, line.text))

        if keyword_hits:
            occurred_on, ocr_confidence, source = keyword_hits[-1]
            return occurred_on, _combined_confidence(0.85, ocr_confidence), source
        if other_hits:
            occurred_on, ocr_confidence, source = other_hits[0]
            return occurred_on, _combined_confidence(0.65, ocr_confidence), source
        return None, 0.0, None

    def _suggest_merchant(
        self,
        lines: tuple[ReceiptOcrLine, ...],
    ) -> tuple[str | None, float, str | None]:
        for index, line in enumerate(lines[:8]):
            if _looks_like_merchant(line.text):
                confidence = 0.5 if index == 0 else 0.4
                return (
                    line.text,
                    _combined_confidence(confidence, line.confidence),
                    line.text,
                )
        return None, 0.0, None

    def _dates_in_text(self, text: str, reference: date) -> list[date]:
        found: list[date] = []
        for match in _ISO_DATE_RE.finditer(text):
            parsed = _try_iso_date(match.group(1), match.group(2), match.group(3))
            if parsed is not None and _date_is_plausible(parsed, reference):
                found.append(parsed)
        for match in _DOT_DATE_RE.finditer(text):
            parsed = _try_dmy(match.group(1), match.group(2), match.group(3))
            if parsed is not None and _date_is_plausible(parsed, reference):
                found.append(parsed)
        for match in _SLASH_DATE_RE.finditer(text):
            parsed = _try_slash_date(
                match.group(1),
                match.group(3),
                match.group(5),
                dayfirst=self._dayfirst,
            )
            if parsed is not None and _date_is_plausible(parsed, reference):
                found.append(parsed)
        for match in _MONTH_NAME_DATE_RE.finditer(text):
            parsed = _try_fuzzy_date(match.group(0), dayfirst=self._dayfirst)
            if parsed is not None and _date_is_plausible(parsed, reference):
                found.append(parsed)
        return found


def _combined_confidence(heuristic: float, ocr_confidence: float) -> float:
    combined = heuristic * (0.5 + 0.5 * ocr_confidence)
    return max(0.0, min(1.0, combined))


def _is_subtotal_line(text: str) -> bool:
    return bool(re.search(r"\bsub\s*total\b", text, flags=re.IGNORECASE))


def _money_amounts(text: str) -> list[float]:
    masked = _mask_date_spans(text)
    amounts: list[float] = []
    for match in _MONEY_RE.finditer(masked):
        whole = match.group(1)
        separator = match.group(2)
        fraction = match.group(3)
        parsed = _parse_money_groups(whole, separator, fraction)
        if parsed is None:
            continue
        if parsed >= 1900 and parsed <= 2100 and parsed == int(parsed):
            continue
        amounts.append(parsed)
    return amounts


def _mask_date_spans(text: str) -> str:
    masked = _ISO_DATE_RE.sub(lambda match: " " * len(match.group(0)), text)
    masked = _DOT_DATE_RE.sub(lambda match: " " * len(match.group(0)), masked)
    masked = _SLASH_DATE_RE.sub(lambda match: " " * len(match.group(0)), masked)
    return _MONTH_NAME_DATE_RE.sub(lambda match: " " * len(match.group(0)), masked)


def _parse_money_groups(whole: str, separator: str | None, fraction: str | None) -> float | None:
    if separator is None or fraction is None:
        digits = whole.replace(",", "").replace(".", "")
        if not digits:
            return None
        return float(int(digits))
    thousands = "." if separator == "," else ","
    integer_part = whole.replace(thousands, "")
    if not integer_part.isdigit() or not fraction.isdigit():
        return None
    return float(f"{int(integer_part)}.{fraction}")


def _try_iso_date(year: str, month: str, day: str) -> date | None:
    return _safe_date(int(year), int(month), int(day))


def _try_dmy(day: str, month: str, year: str) -> date | None:
    return _safe_date(_expand_year(year), int(month), int(day))


def _try_slash_date(first: str, second: str, year: str, *, dayfirst: bool) -> date | None:
    left = int(first)
    right = int(second)
    full_year = _expand_year(year)
    if left > 12:
        return _safe_date(full_year, right, left)
    if right > 12:
        return _safe_date(full_year, left, right)
    if dayfirst:
        return _safe_date(full_year, right, left)
    return _safe_date(full_year, left, right)


def _try_fuzzy_date(token: str, *, dayfirst: bool) -> date | None:
    try:
        parsed = date_parser.parse(token, dayfirst=dayfirst, fuzzy=False)
    except (ValueError, OverflowError, TypeError):
        return None
    return parsed.date()


def _expand_year(year: str) -> int:
    if len(year) == 2:
        value = int(year)
        return 2000 + value if value < 80 else 1900 + value
    return int(year)


def _safe_date(year: int, month: int, day: int) -> date | None:
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _date_is_plausible(value: date, reference: date) -> bool:
    if value > reference + timedelta(days=_MAX_FUTURE_DAYS):
        return False
    return value >= reference - timedelta(days=_MAX_PAST_DAYS)


def _looks_like_merchant(text: str) -> bool:
    if len(text) < 2 or len(text) > 80:
        return False
    if _THANK_YOU_RE.search(text):
        return False
    if _URL_RE.search(text) or _EMAIL_RE.search(text) or _PHONE_RE.search(text):
        return False
    if _STREET_RE.search(text) or _POSTAL_RE.search(text):
        return False
    if _ISO_DATE_RE.search(text) or _DOT_DATE_RE.search(text) or _SLASH_DATE_RE.search(text):
        return False
    if _MONTH_NAME_DATE_RE.search(text) or _DATE_KEYWORD_RE.search(text):
        return False
    if _TOTAL_KEYWORD_RE.search(text) or _IGNORE_AMOUNT_RE.search(text):
        return False
    if _money_amounts(text) and not re.search(r"[A-Za-z]{3,}", text):
        return False
    digit_count = sum(char.isdigit() for char in text)
    return digit_count < max(3, len(text) // 2)
