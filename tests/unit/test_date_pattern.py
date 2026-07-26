from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import patch

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.domain.date_pattern import (
    ParsedPattern,
    PatternType,
    describe_pattern,
    expand_all,
    expand_pattern,
    parse_pattern,
)
from src.domain.entities import Entry, EntryType, FinancialEvent
from src.domain.exceptions import DatePatternParseError


def _entry(
    date_pattern: str,
    *,
    entry_id: str = "entry-1",
    name: str = "Test",
    amount: float = 100.0,
    is_active: bool = True,
) -> Entry:
    return Entry(
        id=entry_id,
        plan_id="plan-1",
        entry_type=EntryType.EXPENSE,
        name=name,
        date_pattern=date_pattern,
        amount=amount,
        currency="USD",
        is_active=is_active,
        created_at="2026-01-01T00:00:00",
    )


# --- parse_pattern ---


@pytest.mark.unit
@pytest.mark.parametrize(
    ("raw", "expected_type", "expected_day", "expected_month", "expected_year"),
    [
        ("...", PatternType.DAILY, None, None, None),
        ("1..", PatternType.MONTHLY, 1, None, None),
        ("10..", PatternType.MONTHLY, 10, None, None),
        ("31..", PatternType.MONTHLY, 31, None, None),
        ("1.1.", PatternType.YEARLY, 1, 1, None),
        ("10.2.", PatternType.YEARLY, 10, 2, None),
        ("29.2.", PatternType.YEARLY, 29, 2, None),
        ("1.1.2000", PatternType.ONE_TIME, 1, 1, 2000),
        ("10.02.2026", PatternType.ONE_TIME, 10, 2, 2026),
        ("31.12.2099", PatternType.ONE_TIME, 31, 12, 2099),
    ],
)
def test_parse_pattern_valid(
    raw: str,
    expected_type: PatternType,
    expected_day: int | None,
    expected_month: int | None,
    expected_year: int | None,
) -> None:
    result = parse_pattern(raw)
    assert result.type == expected_type
    assert result.day == expected_day
    assert result.month == expected_month
    assert result.year == expected_year


@pytest.mark.unit
@pytest.mark.parametrize(
    "raw",
    [
        "",
        ".",
        "..",
        "10.",
        "10.02",
        "abc",
        "32..",
        "0..",
        "10.0.",
        "10.13.",
        "10.02.20",
    ],
)
def test_parse_pattern_invalid(raw: str) -> None:
    with pytest.raises(DatePatternParseError):
        parse_pattern(raw)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ("32..", "Day out of range"),
        ("0..", "Day out of range"),
        ("10.0.", "Month out of range"),
        ("10.13.", "Month out of range"),
    ],
)
def test_parse_pattern_out_of_range(raw: str, message: str) -> None:
    with pytest.raises(DatePatternParseError, match=message):
        parse_pattern(raw)


# --- describe_pattern ---


@pytest.mark.unit
def test_describe_pattern_daily() -> None:
    assert describe_pattern(ParsedPattern(type=PatternType.DAILY)) == "Every day"


@pytest.mark.unit
@pytest.mark.parametrize(
    ("day", "expected_suffix"),
    [
        (1, "1st"),
        (2, "2nd"),
        (3, "3rd"),
        (4, "4th"),
        (11, "11th"),
        (12, "12th"),
        (13, "13th"),
        (21, "21st"),
        (22, "22nd"),
        (23, "23rd"),
    ],
)
def test_describe_pattern_monthly_ordinals(day: int, expected_suffix: str) -> None:
    pattern = ParsedPattern(type=PatternType.MONTHLY, day=day)
    assert describe_pattern(pattern) == f"Monthly on the {expected_suffix}"


@pytest.mark.unit
@pytest.mark.parametrize(
    ("day", "month", "expected"),
    [
        (10, 2, "Yearly on 10 Feb"),
        (1, 12, "Yearly on 1 Dec"),
    ],
)
def test_describe_pattern_yearly(day: int, month: int, expected: str) -> None:
    pattern = ParsedPattern(type=PatternType.YEARLY, day=day, month=month)
    assert describe_pattern(pattern) == expected


@pytest.mark.unit
def test_describe_pattern_one_time() -> None:
    pattern = ParsedPattern(type=PatternType.ONE_TIME, day=10, month=2, year=2026)
    assert describe_pattern(pattern) == "Once on 10 Feb 2026"


@pytest.mark.unit
@pytest.mark.parametrize(
    ("pattern", "message"),
    [
        (ParsedPattern(type=PatternType.MONTHLY), "Monthly pattern requires a day"),
        (ParsedPattern(type=PatternType.YEARLY, day=1), "Yearly pattern requires day and month"),
        (ParsedPattern(type=PatternType.YEARLY, month=1), "Yearly pattern requires day and month"),
        (
            ParsedPattern(type=PatternType.ONE_TIME, day=1, month=1),
            "One-time pattern requires day, month, and year",
        ),
        (
            ParsedPattern(type=PatternType.ONE_TIME, day=1, year=2026),
            "One-time pattern requires day, month, and year",
        ),
        (
            ParsedPattern(type=PatternType.ONE_TIME, month=1, year=2026),
            "One-time pattern requires day, month, and year",
        ),
    ],
)
def test_describe_pattern_missing_fields(pattern: ParsedPattern, message: str) -> None:
    with pytest.raises(DatePatternParseError, match=message):
        describe_pattern(pattern)


# --- expand_pattern ---


@pytest.mark.unit
def test_expand_pattern_empty_window() -> None:
    entry = _entry("...")
    assert expand_pattern(entry, date(2026, 3, 1), date(2026, 2, 1)) == []


@pytest.mark.unit
def test_expand_pattern_daily() -> None:
    entry = _entry("...")
    events = expand_pattern(entry, date(2026, 1, 1), date(2026, 1, 3))
    assert len(events) == 3
    assert [e.date for e in events] == [
        date(2026, 1, 1),
        date(2026, 1, 2),
        date(2026, 1, 3),
    ]


@pytest.mark.unit
def test_expand_pattern_monthly() -> None:
    entry = _entry("10..")
    events = expand_pattern(entry, date(2026, 1, 1), date(2026, 3, 31))
    assert [e.date for e in events] == [
        date(2026, 1, 10),
        date(2026, 2, 10),
        date(2026, 3, 10),
    ]


@pytest.mark.unit
def test_expand_pattern_monthly_skips_invalid_days() -> None:
    entry = _entry("31..")
    events = expand_pattern(entry, date(2026, 1, 1), date(2026, 3, 31))
    assert [e.date for e in events] == [date(2026, 1, 31), date(2026, 3, 31)]


@pytest.mark.unit
def test_expand_pattern_monthly_respects_start_boundary() -> None:
    entry = _entry("10..")
    events = expand_pattern(entry, date(2026, 1, 15), date(2026, 3, 31))
    assert [e.date for e in events] == [date(2026, 2, 10), date(2026, 3, 10)]


@pytest.mark.unit
def test_expand_pattern_yearly() -> None:
    entry = _entry("15.6.")
    events = expand_pattern(entry, date(2026, 1, 1), date(2028, 12, 31))
    assert [e.date for e in events] == [
        date(2026, 6, 15),
        date(2027, 6, 15),
        date(2028, 6, 15),
    ]


@pytest.mark.unit
def test_expand_pattern_yearly_leap_day_skips_non_leap_years() -> None:
    entry = _entry("29.2.")
    events = expand_pattern(entry, date(2024, 1, 1), date(2028, 12, 31))
    assert [e.date for e in events] == [date(2024, 2, 29), date(2028, 2, 29)]


@pytest.mark.unit
def test_expand_pattern_one_time_inside_window() -> None:
    entry = _entry("10.02.2026")
    events = expand_pattern(entry, date(2026, 1, 1), date(2026, 12, 31))
    assert len(events) == 1
    assert events[0].date == date(2026, 2, 10)


@pytest.mark.unit
def test_expand_pattern_one_time_before_window() -> None:
    entry = _entry("10.02.2026")
    events = expand_pattern(entry, date(2026, 3, 1), date(2026, 12, 31))
    assert events == []


@pytest.mark.unit
def test_expand_pattern_one_time_after_window() -> None:
    entry = _entry("10.02.2026")
    events = expand_pattern(entry, date(2025, 1, 1), date(2025, 12, 31))
    assert events == []


@pytest.mark.unit
def test_expand_pattern_one_time_invalid_calendar_date() -> None:
    entry = _entry("31.02.2026")
    events = expand_pattern(entry, date(2026, 1, 1), date(2026, 12, 31))
    assert events == []


@pytest.mark.unit
def test_expand_pattern_event_fields() -> None:
    entry = _entry("10.02.2026", name="Rent", amount=500.0)
    events = expand_pattern(entry, date(2026, 1, 1), date(2026, 12, 31))
    event = events[0]
    assert event.entry_id == entry.id
    assert event.entry_name == "Rent"
    assert event.amount == 500.0
    assert event.currency == "USD"
    assert event.type == EntryType.EXPENSE


@pytest.mark.unit
@pytest.mark.parametrize(
    ("pattern_type", "pattern", "message"),
    [
        (
            PatternType.MONTHLY,
            ParsedPattern(type=PatternType.MONTHLY),
            "Monthly pattern requires a day",
        ),
        (
            PatternType.YEARLY,
            ParsedPattern(type=PatternType.YEARLY, day=1),
            "Yearly pattern requires day and month",
        ),
        (
            PatternType.ONE_TIME,
            ParsedPattern(type=PatternType.ONE_TIME, day=1, month=1),
            "One-time pattern requires day, month, and year",
        ),
    ],
)
def test_expand_pattern_missing_parsed_fields(
    pattern_type: PatternType,
    pattern: ParsedPattern,
    message: str,
) -> None:
    entry = _entry("...")
    with patch("src.domain.date_pattern.parse_pattern", return_value=pattern):
        with pytest.raises(DatePatternParseError, match=message):
            expand_pattern(entry, date(2026, 1, 1), date(2026, 12, 31))


# --- expand_all ---


@pytest.mark.unit
def test_expand_all_sorts_by_date_then_entry_id() -> None:
    entries = [
        _entry("10.02.2026", entry_id="b"),
        _entry("10.02.2026", entry_id="a"),
        _entry("15.02.2026", entry_id="c"),
    ]
    events = expand_all(entries, date(2026, 1, 1), date(2026, 12, 31))
    assert [e.entry_id for e in events] == ["a", "b", "c"]


@pytest.mark.unit
def test_expand_all_empty_entries() -> None:
    assert expand_all([], date(2026, 1, 1), date(2026, 12, 31)) == []


@pytest.mark.unit
def test_expand_all_skips_inactive_entries() -> None:
    entries = [
        _entry("1..", entry_id="active"),
        _entry("1..", entry_id="inactive", is_active=False),
    ]
    events = expand_all(entries, date(2026, 1, 1), date(2026, 3, 31))
    assert all(event.entry_id == "active" for event in events)
    assert len(events) == 3


# --- Hypothesis: parser properties ---


@pytest.mark.unit
@given(day=st.integers(min_value=1, max_value=28))
@settings(max_examples=200)
def test_hypothesis_parse_monthly(day: int) -> None:
    result = parse_pattern(f"{day}..")
    assert result == ParsedPattern(type=PatternType.MONTHLY, day=day)


@pytest.mark.unit
@given(day=st.integers(min_value=1, max_value=28), month=st.integers(min_value=1, max_value=12))
@settings(max_examples=200)
def test_hypothesis_parse_yearly(day: int, month: int) -> None:
    result = parse_pattern(f"{day}.{month}.")
    assert result == ParsedPattern(type=PatternType.YEARLY, day=day, month=month)


@pytest.mark.unit
@given(
    day=st.integers(min_value=1, max_value=28),
    month=st.integers(min_value=1, max_value=12),
    year=st.integers(min_value=2000, max_value=2099),
)
@settings(max_examples=200)
def test_hypothesis_parse_one_time(day: int, month: int, year: int) -> None:
    result = parse_pattern(f"{day}.{month}.{year}")
    assert result == ParsedPattern(
        type=PatternType.ONE_TIME,
        day=day,
        month=month,
        year=year,
    )


# --- Hypothesis: expander properties ---


@pytest.mark.unit
@given(
    start=st.dates(min_value=date(2000, 1, 1), max_value=date(2090, 1, 1)),
    span_days=st.integers(min_value=0, max_value=365),
)
@settings(max_examples=200)
def test_hypothesis_expand_daily_count(start: date, span_days: int) -> None:
    end = start + timedelta(days=span_days)
    entry = _entry("...")
    events = expand_pattern(entry, start, end)
    assert len(events) == span_days + 1


@pytest.mark.unit
@given(
    day=st.integers(min_value=1, max_value=28),
    month_count=st.integers(min_value=1, max_value=24),
)
@settings(max_examples=200)
def test_hypothesis_expand_monthly_count(day: int, month_count: int) -> None:
    start = date(2026, 1, 1)
    end_month = start.month + month_count - 1
    end_year = start.year + (end_month - 1) // 12
    end_month = ((end_month - 1) % 12) + 1
    end = date(end_year, end_month, 28)
    entry = _entry(f"{day}..")
    events = expand_pattern(entry, start, end)
    assert len(events) == month_count


@pytest.mark.unit
@given(
    day=st.integers(min_value=1, max_value=28),
    month=st.integers(min_value=1, max_value=12),
    year=st.integers(min_value=2020, max_value=2030),
)
@settings(max_examples=200)
def test_hypothesis_expand_one_time_inside_window(
    day: int,
    month: int,
    year: int,
) -> None:
    event_date = date(year, month, day)
    entry = _entry(f"{day}.{month}.{year}")
    events = expand_pattern(entry, event_date, event_date)
    assert len(events) == 1
    assert events[0].date == event_date


@pytest.mark.unit
@given(
    day=st.integers(min_value=1, max_value=28),
    month=st.integers(min_value=1, max_value=12),
    year=st.integers(min_value=2020, max_value=2030),
)
@settings(max_examples=200)
def test_hypothesis_expand_one_time_outside_window(
    day: int,
    month: int,
    year: int,
) -> None:
    event_date = date(year, month, day)
    entry = _entry(f"{day}.{month}.{year}")
    events = expand_pattern(entry, event_date + timedelta(days=1), event_date + timedelta(days=30))
    assert events == []


@pytest.mark.unit
@given(
    raw_pattern=st.sampled_from(["...", "15..", "10.6.", "10.6.2026"]),
    start=st.dates(min_value=date(2020, 1, 1), max_value=date(2030, 6, 1)),
    span_days=st.integers(min_value=0, max_value=400),
)
@settings(max_examples=200)
def test_hypothesis_expand_events_within_window(
    raw_pattern: str,
    start: date,
    span_days: int,
) -> None:
    end = start + timedelta(days=span_days)
    entry = _entry(raw_pattern)
    events = expand_pattern(entry, start, end)
    for event in events:
        assert start <= event.date <= end
        assert isinstance(event, FinancialEvent)
