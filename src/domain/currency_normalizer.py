from __future__ import annotations

from src.domain.entities import ExchangeRate, FinancialEvent, NormalizedEvent
from src.domain.exceptions import CurrencyConversionError


def _find_rate(
    from_currency: str,
    to_currency: str,
    exchange_rates: list[ExchangeRate],
) -> ExchangeRate | None:
    for rate in exchange_rates:
        if rate.from_currency == from_currency and rate.to_currency == to_currency:
            return rate
    return None


def normalize(
    event: FinancialEvent,
    base_currency: str,
    exchange_rates: list[ExchangeRate],
) -> float:
    """Convert event.amount to base_currency using the global rate lookup."""
    return convert_amount(event.amount, event.currency, base_currency, exchange_rates)


def convert_amount(
    amount: float,
    from_currency: str,
    to_currency: str,
    exchange_rates: list[ExchangeRate],
) -> float:
    """Convert amount between currencies using direct or inverse rate lookup."""
    if from_currency == to_currency:
        return amount

    direct = _find_rate(from_currency, to_currency, exchange_rates)
    if direct is not None:
        return amount * direct.rate

    inverse = _find_rate(to_currency, from_currency, exchange_rates)
    if inverse is not None:
        if inverse.rate == 0:
            msg = f"Exchange rate for {to_currency} → {from_currency} is zero"
            raise CurrencyConversionError(msg)
        return amount / inverse.rate

    msg = f"No exchange rate found for {from_currency} → {to_currency}"
    raise CurrencyConversionError(msg)


def display_currencies(
    exchange_rates: list[ExchangeRate], *, base_currency: str = "USD"
) -> list[str]:
    """Return base currency plus foreign currencies with a rate to base."""
    foreign = sorted(
        {
            rate.from_currency
            for rate in exchange_rates
            if rate.to_currency == base_currency and rate.from_currency != base_currency
        }
    )
    return [base_currency, *foreign]


def normalize_all(
    events: list[FinancialEvent],
    base_currency: str,
    exchange_rates: list[ExchangeRate],
) -> list[NormalizedEvent]:
    """Normalize a batch of events to the plan's base currency."""
    return [
        NormalizedEvent(
            entry_id=event.entry_id,
            entry_name=event.entry_name,
            date=event.date,
            type=event.type,
            normalized_amount=normalize(event, base_currency, exchange_rates),
            base_currency=base_currency,
            category=event.category,
        )
        for event in events
    ]
