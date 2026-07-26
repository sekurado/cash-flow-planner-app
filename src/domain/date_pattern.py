from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum

from dateutil.relativedelta import relativedelta

from src.domain.entities import Entry, FinancialEvent
from src.domain.exceptions import DatePatternParseError

_DAILY_RE = re.compile(r"^\.\.\.$")
_MONTHLY_RE = re.compile(r"^(\d{1,2})\.\.$")
_YEARLY_RE = re.compile(r"^(\d{1,2})\.(\d{1,2})\.$")
_ONE_TIME_RE = re.compile(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})$")

_MONTH_ABBREV = (
    "",
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)


class PatternType(StrEnum):
    DAILY = "daily"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    ONE_TIME = "one-time"


@dataclass(frozen=True)
class ParsedPattern:
    type: PatternType
    day: int | None = None
    month: int | None = None
    year: int | None = None


def _validate_day(day: int) -> None:
    if not 1 <= day <= 31:
        msg = f"Day out of range: {day}"
        raise DatePatternParseError(msg)


def _validate_month(month: int) -> None:
    if not 1 <= month <= 12:
        msg = f"Month out of range: {month}"
        raise DatePatternParseError(msg)


def _ordinal(day: int) -> str:
    if 11 <= (day % 100) <= 13:
        return f"{day}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{day}{suffix}"


def parse_pattern(raw: str) -> ParsedPattern:
    if _DAILY_RE.match(raw):
        return ParsedPattern(type=PatternType.DAILY)

    if match := _MONTHLY_RE.match(raw):
        day = int(match.group(1))
        _validate_day(day)
        return ParsedPattern(type=PatternType.MONTHLY, day=day)

    if match := _YEARLY_RE.match(raw):
        day = int(match.group(1))
        month = int(match.group(2))
        _validate_day(day)
        _validate_month(month)
        return ParsedPattern(type=PatternType.YEARLY, day=day, month=month)

    if match := _ONE_TIME_RE.match(raw):
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))
        _validate_day(day)
        _validate_month(month)
        return ParsedPattern(type=PatternType.ONE_TIME, day=day, month=month, year=year)

    msg = f"Invalid date pattern: {raw!r}"
    raise DatePatternParseError(msg)


def pattern_description_template(pattern: ParsedPattern) -> tuple[str, tuple[str, ...]]:
    """Return a Qt-style message template and substitution arguments."""
    match pattern.type:
        case PatternType.DAILY:
            return ("Every day", ())
        case PatternType.MONTHLY:
            if pattern.day is None:
                msg = "Monthly pattern requires a day"
                raise DatePatternParseError(msg)
            return ("Monthly on the %1", (_ordinal(pattern.day),))
        case PatternType.YEARLY:
            if pattern.day is None or pattern.month is None:
                msg = "Yearly pattern requires day and month"
                raise DatePatternParseError(msg)
            return (
                "Yearly on %1 %2",
                (str(pattern.day), _MONTH_ABBREV[pattern.month]),
            )
        case PatternType.ONE_TIME:  # pragma: no branch
            if pattern.day is None or pattern.month is None or pattern.year is None:
                msg = "One-time pattern requires day, month, and year"
                raise DatePatternParseError(msg)
            return (
                "Once on %1 %2 %3",
                (
                    str(pattern.day),
                    _MONTH_ABBREV[pattern.month],
                    str(pattern.year),
                ),
            )


def describe_pattern(pattern: ParsedPattern) -> str:
    template, args = pattern_description_template(pattern)
    if not args:
        return template
    result = template
    for index, arg in enumerate(args, start=1):
        result = result.replace(f"%{index}", arg)
    return result


def _safe_date(year: int, month: int, day: int) -> date | None:
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _make_event(entry: Entry, event_date: date) -> FinancialEvent:
    return FinancialEvent(
        entry_id=entry.id,
        entry_name=entry.name,
        date=event_date,
        type=entry.entry_type,
        amount=entry.amount,
        currency=entry.currency,
        category=entry.category,
    )


def expand_pattern(entry: Entry, start: date, end: date) -> list[FinancialEvent]:
    if start > end:
        return []

    pattern = parse_pattern(entry.date_pattern)
    events: list[FinancialEvent] = []

    match pattern.type:
        case PatternType.DAILY:
            cursor = start
            while cursor <= end:
                events.append(_make_event(entry, cursor))
                cursor += timedelta(days=1)

        case PatternType.MONTHLY:
            if pattern.day is None:
                msg = "Monthly pattern requires a day"
                raise DatePatternParseError(msg)
            day = pattern.day
            month_cursor = date(start.year, start.month, 1)
            while month_cursor <= end:
                event_date = _safe_date(month_cursor.year, month_cursor.month, day)
                if event_date is not None and start <= event_date <= end:
                    events.append(_make_event(entry, event_date))
                month_cursor += relativedelta(months=1)

        case PatternType.YEARLY:
            if pattern.day is None or pattern.month is None:
                msg = "Yearly pattern requires day and month"
                raise DatePatternParseError(msg)
            day, month = pattern.day, pattern.month
            year = start.year
            while year <= end.year:
                event_date = _safe_date(year, month, day)
                if event_date is not None and start <= event_date <= end:
                    events.append(_make_event(entry, event_date))
                year += 1

        case PatternType.ONE_TIME:  # pragma: no branch
            if pattern.day is None or pattern.month is None or pattern.year is None:
                msg = "One-time pattern requires day, month, and year"
                raise DatePatternParseError(msg)
            event_date = _safe_date(pattern.year, pattern.month, pattern.day)
            if event_date is not None and start <= event_date <= end:
                events.append(_make_event(entry, event_date))

    return events


def expand_all(entries: list[Entry], start: date, end: date) -> list[FinancialEvent]:
    events: list[FinancialEvent] = []
    for entry in entries:
        if not entry.is_active:
            continue
        events.extend(expand_pattern(entry, start, end))
    events.sort(key=lambda e: (e.date, e.entry_id))
    return events
