from __future__ import annotations

from collections.abc import Iterable

from src.domain.entities import ExchangeRate


def _rate_for_conversion(
    from_currency: str,
    to_currency: str,
    rates_by_pair: dict[tuple[str, str], ExchangeRate],
) -> ExchangeRate | None:
    if from_currency == to_currency:
        return None
    direct = rates_by_pair.get((from_currency, to_currency))
    if direct is not None:
        return direct
    return rates_by_pair.get((to_currency, from_currency))


def rates_used_for_export(
    *,
    entry_currencies: Iterable[str],
    base_currency: str,
    display_currency: str,
    exchange_rates: list[ExchangeRate] | tuple[ExchangeRate, ...],
) -> tuple[ExchangeRate, ...]:
    """Return exchange-rate rows needed to normalize entries and convert to display currency."""
    rates_by_pair = {(rate.from_currency, rate.to_currency): rate for rate in exchange_rates}
    needed: list[ExchangeRate] = []
    seen: set[tuple[str, str]] = set()

    def add_conversion(from_currency: str, to_currency: str) -> None:
        rate = _rate_for_conversion(from_currency, to_currency, rates_by_pair)
        if rate is None:
            return
        key = (rate.from_currency, rate.to_currency)
        if key in seen:
            return
        seen.add(key)
        needed.append(rate)

    for currency in entry_currencies:
        if currency != base_currency:
            add_conversion(currency, base_currency)

    if display_currency != base_currency:
        add_conversion(base_currency, display_currency)

    needed.sort(key=lambda rate: (rate.from_currency, rate.to_currency))
    return tuple(needed)
