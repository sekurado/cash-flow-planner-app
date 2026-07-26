from __future__ import annotations

from datetime import date

import pytest

from src.domain.currency_normalizer import (
    convert_amount,
    display_currencies,
    normalize,
    normalize_all,
)
from src.domain.entities import EntryType, ExchangeRate, FinancialEvent, NormalizedEvent
from src.domain.exceptions import CurrencyConversionError


def _event(
    *,
    amount: float = 100.0,
    currency: str = "EUR",
    event_date: date = date(2026, 3, 15),
    entry_id: str = "entry-1",
    entry_name: str = "Salary",
    entry_type: EntryType = EntryType.INCOME,
) -> FinancialEvent:
    return FinancialEvent(
        entry_id=entry_id,
        entry_name=entry_name,
        date=event_date,
        type=entry_type,
        amount=amount,
        currency=currency,
    )


def _rate(
    *,
    from_currency: str = "EUR",
    to_currency: str = "USD",
    rate: float = 1.1,
    updated_at: str = "2026-01-01T00:00:00+00:00",
) -> ExchangeRate:
    return ExchangeRate(
        from_currency=from_currency,
        to_currency=to_currency,
        rate=rate,
        updated_at=updated_at,
    )


@pytest.mark.unit
def test_normalize_direct_rate() -> None:
    event = _event(amount=100.0, currency="EUR")
    rates = [_rate(from_currency="EUR", to_currency="USD", rate=1.1)]

    assert normalize(event, "USD", rates) == pytest.approx(110.0)


@pytest.mark.unit
def test_normalize_same_currency_passthrough() -> None:
    event = _event(amount=250.0, currency="USD")

    assert normalize(event, "USD", []) == pytest.approx(250.0)


@pytest.mark.unit
def test_normalize_raises_when_rate_missing() -> None:
    event = _event(amount=100.0, currency="EUR", event_date=date(2026, 3, 1))

    with pytest.raises(CurrencyConversionError, match="EUR → USD"):
        normalize(event, "USD", [])


@pytest.mark.unit
def test_convert_amount_uses_inverse_rate() -> None:
    rates = [_rate(from_currency="EUR", to_currency="USD", rate=1.1)]

    assert convert_amount(110.0, "USD", "EUR", rates) == pytest.approx(100.0)


@pytest.mark.unit
def test_convert_amount_same_currency_passthrough() -> None:
    assert convert_amount(250.0, "USD", "USD", []) == pytest.approx(250.0)


@pytest.mark.unit
def test_convert_amount_raises_when_rate_missing() -> None:
    with pytest.raises(CurrencyConversionError, match="USD → EUR"):
        convert_amount(100.0, "USD", "EUR", [])


@pytest.mark.unit
def test_display_currencies_includes_usd_and_foreign_rates() -> None:
    rates = [
        _rate(from_currency="EUR", to_currency="USD", rate=1.1),
        _rate(from_currency="GBP", to_currency="USD", rate=1.25),
        _rate(from_currency="GBP", to_currency="EUR", rate=0.85),
    ]

    assert display_currencies(rates) == ["USD", "EUR", "GBP"]


@pytest.mark.unit
def test_normalize_all_mixed_currencies() -> None:
    events = [
        _event(
            entry_id="e1",
            entry_name="EUR income",
            amount=100.0,
            currency="EUR",
            event_date=date(2026, 3, 1),
        ),
        _event(
            entry_id="e2",
            entry_name="USD expense",
            amount=50.0,
            currency="USD",
            event_date=date(2026, 3, 2),
            entry_type=EntryType.EXPENSE,
        ),
        _event(
            entry_id="e3",
            entry_name="GBP income",
            amount=80.0,
            currency="GBP",
            event_date=date(2026, 3, 3),
        ),
    ]
    rates = [
        _rate(
            from_currency="EUR",
            to_currency="USD",
            rate=1.1,
        ),
        _rate(
            from_currency="GBP",
            to_currency="USD",
            rate=1.25,
        ),
    ]

    result = normalize_all(events, "USD", rates)

    assert len(result) == 3
    assert all(isinstance(item, NormalizedEvent) for item in result)
    assert result[0].normalized_amount == pytest.approx(110.0)
    assert result[0].base_currency == "USD"
    assert result[1].normalized_amount == pytest.approx(50.0)
    assert result[2].normalized_amount == pytest.approx(100.0)
    assert result[0].entry_id == "e1"
    assert result[1].type == EntryType.EXPENSE
    assert result[2].category is None
