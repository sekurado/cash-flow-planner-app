from __future__ import annotations

import pytest

from src.domain.entities import ExchangeRate
from src.export.rate_selection import rates_used_for_export


def _rate(from_currency: str, to_currency: str, rate: float) -> ExchangeRate:
    return ExchangeRate(
        from_currency=from_currency,
        to_currency=to_currency,
        rate=rate,
        updated_at="2026-01-01T00:00:00Z",
    )


_CACHE = (
    _rate("EUR", "USD", 1.1),
    _rate("GBP", "USD", 1.25),
    _rate("JPY", "USD", 0.0067),
)


@pytest.mark.unit
def test_rates_used_for_export_includes_only_entry_foreign_currencies() -> None:
    rates = rates_used_for_export(
        entry_currencies={"EUR", "USD"},
        base_currency="USD",
        display_currency="USD",
        exchange_rates=_CACHE,
    )

    assert rates == (_rate("EUR", "USD", 1.1),)


@pytest.mark.unit
def test_rates_used_for_export_empty_when_all_entries_match_base_and_display() -> None:
    rates = rates_used_for_export(
        entry_currencies={"USD"},
        base_currency="USD",
        display_currency="USD",
        exchange_rates=_CACHE,
    )

    assert rates == ()


@pytest.mark.unit
def test_rates_used_for_export_includes_base_to_display_pair() -> None:
    rates = rates_used_for_export(
        entry_currencies={"USD"},
        base_currency="USD",
        display_currency="EUR",
        exchange_rates=(_rate("USD", "EUR", 0.92), *_CACHE),
    )

    assert rates == (_rate("USD", "EUR", 0.92),)


@pytest.mark.unit
def test_rates_used_for_export_uses_inverse_rate_when_direct_missing() -> None:
    rates = rates_used_for_export(
        entry_currencies={"EUR"},
        base_currency="USD",
        display_currency="USD",
        exchange_rates=(_rate("USD", "EUR", 0.92),),
    )

    assert rates == (_rate("USD", "EUR", 0.92),)


@pytest.mark.unit
def test_rates_used_for_export_combines_entry_and_display_conversions() -> None:
    rates = rates_used_for_export(
        entry_currencies={"EUR", "USD"},
        base_currency="USD",
        display_currency="GBP",
        exchange_rates=(
            _rate("EUR", "USD", 1.1),
            _rate("USD", "GBP", 0.79),
            _rate("JPY", "USD", 0.0067),
        ),
    )

    assert rates == (
        _rate("EUR", "USD", 1.1),
        _rate("USD", "GBP", 0.79),
    )
