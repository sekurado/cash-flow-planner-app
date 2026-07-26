"""Counterfactual simulation helpers for cash-flow suggestion analyzers."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import date, timedelta

from src.domain.currency_normalizer import normalize_all
from src.domain.date_pattern import expand_all
from src.domain.entities import Entry, EntryType, ExchangeRate, SimulationParams, SimulationResult
from src.domain.simulation_engine import SimulationEngine

_BINARY_SEARCH_TOLERANCE = 0.01
_MAX_BINARY_SEARCH_ITERATIONS = 64


def simulate_entries(
    entries: Sequence[Entry],
    params: SimulationParams,
    *,
    plan_id: str = "",
    exchange_rates: Sequence[ExchangeRate] | None = None,
) -> SimulationResult:
    """Expand, normalize, and run a projection for the given cash flows."""
    events = expand_all(list(entries), params.start_date, params.end_date)
    rates = list(exchange_rates or ())
    normalized = normalize_all(events, params.base_currency, rates)
    return SimulationEngine.run(normalized, params, plan_id=plan_id)


def minimum_opening_balance_buffer(result: SimulationResult) -> float:
    """Return the minimum initial-balance increase that keeps all daily balances non-negative."""
    if not result.daily_balances:
        return 0.0
    min_closing = min(day.closing_balance for day in result.daily_balances)
    return max(0.0, -min_closing)


def horizon_month_count(params: SimulationParams) -> float:
    """Approximate month count for the projection window (minimum 1)."""
    day_count = (params.end_date - params.start_date).days + 1
    return max(1.0, day_count / 30.0)


def binary_search_minimum(
    *,
    low: float,
    high: float,
    predicate: Callable[[float], bool],
) -> float | None:
    """Return the smallest value in [low, high] where predicate is true, or None."""
    if low > high:
        return None
    if not predicate(high):
        return None

    best = high
    left = low
    right = high
    for _ in range(_MAX_BINARY_SEARCH_ITERATIONS):
        if right - left <= _BINARY_SEARCH_TOLERANCE:
            break
        mid = (left + right) / 2.0
        if predicate(mid):
            best = mid
            right = mid
        else:
            left = mid
    return best


def binary_search_maximum(
    *,
    low: float,
    high: float,
    predicate: Callable[[float], bool],
) -> float | None:
    """Return the largest value in [low, high] where predicate is true, or None."""
    if low > high:
        return None
    if not predicate(low):
        return None
    if predicate(high):
        return high

    best = low
    left = low
    right = high
    for _ in range(_MAX_BINARY_SEARCH_ITERATIONS):
        if right - left <= _BINARY_SEARCH_TOLERANCE:
            break
        mid = (left + right) / 2.0
        if predicate(mid):
            best = mid
            left = mid
        else:
            right = mid
    return best


def apply_monthly_expense_pressure(
    entries: Sequence[Entry],
    monthly_pressure: float,
) -> list[Entry]:
    """Spread ``monthly_pressure`` evenly across active recurring expense cash flows."""
    recurring_expenses = [
        entry
        for entry in entries
        if entry.is_active
        and entry.entry_type == EntryType.EXPENSE
        and _is_recurring_pattern(entry.date_pattern)
    ]
    if not recurring_expenses:
        return list(entries)

    per_entry_pressure = monthly_pressure / len(recurring_expenses)
    pressured_ids = {entry.id for entry in recurring_expenses}
    patched: list[Entry] = []
    for entry in entries:
        if entry.id in pressured_ids:
            patched.append(
                entry.model_copy(update={"amount": entry.amount + per_entry_pressure}),
            )
        else:
            patched.append(entry)
    return patched


def average_monthly_expense(result: SimulationResult) -> float:
    """Return average monthly expense over the projection horizon."""
    months = horizon_month_count(result.params)
    return result.total_expense / months


def average_monthly_income(result: SimulationResult) -> float:
    """Return average monthly income over the projection horizon."""
    months = horizon_month_count(result.params)
    return result.total_income / months


def average_monthly_burn(result: SimulationResult) -> float:
    """Return average monthly net cash outflow (expense minus income, floored at zero)."""
    return max(0.0, average_monthly_expense(result) - average_monthly_income(result))


def apply_uniform_expense_cut(entries: Sequence[Entry], cut_percent: float) -> list[Entry]:
    """Return entries with recurring expenses reduced by ``cut_percent`` (0–100)."""
    factor = max(0.0, 1.0 - cut_percent / 100.0)
    patched: list[Entry] = []
    for entry in entries:
        if (
            entry.is_active
            and entry.entry_type == EntryType.EXPENSE
            and _is_recurring_pattern(entry.date_pattern)
        ):
            patched.append(entry.model_copy(update={"amount": entry.amount * factor}))
        else:
            patched.append(entry)
    return patched


def apply_entry_amount_delta(entries: Sequence[Entry], entry_id: str, delta: float) -> list[Entry]:
    """Return entries with one cash flow's amount adjusted by ``delta``."""
    patched: list[Entry] = []
    for entry in entries:
        if entry.id == entry_id:
            patched.append(entry.model_copy(update={"amount": max(0.0, entry.amount + delta)}))
        else:
            patched.append(entry)
    return patched


def apply_income_boost(entries: Sequence[Entry], monthly_boost: float) -> list[Entry]:
    """Spread ``monthly_boost`` evenly across active recurring income cash flows."""
    recurring_income = [
        entry
        for entry in entries
        if entry.is_active
        and entry.entry_type == EntryType.INCOME
        and _is_recurring_pattern(entry.date_pattern)
    ]
    if not recurring_income:
        return list(entries)

    per_entry_boost = monthly_boost / len(recurring_income)
    boosted_ids = {entry.id for entry in recurring_income}
    patched: list[Entry] = []
    for entry in entries:
        if entry.id in boosted_ids:
            patched.append(
                entry.model_copy(update={"amount": entry.amount + per_entry_boost}),
            )
        else:
            patched.append(entry)
    return patched


def apply_opening_balance(
    params: SimulationParams, target_initial_balance: float
) -> SimulationParams:
    """Return params with an updated opening balance."""
    return SimulationParams(
        start_date=params.start_date,
        end_date=params.end_date,
        initial_balance=target_initial_balance,
        base_currency=params.base_currency,
    )


def clears_deficit(
    entries: Sequence[Entry],
    params: SimulationParams,
    *,
    plan_id: str,
) -> bool:
    """Return True when re-simulation shows no cash shortfall through the horizon."""
    counterfactual = simulate_entries(entries, params, plan_id=plan_id)
    return counterfactual.first_deficit_date is None


def days_before_deficit_window(deficit_date: date, *, days: int = 30) -> tuple[date, date]:
    """Return inclusive date bounds for the pre-shortfall lookback window."""
    window_start = deficit_date - timedelta(days=days)
    return window_start, deficit_date


def _is_recurring_pattern(date_pattern: str) -> bool:
    from src.domain.date_pattern import PatternType, parse_pattern

    return parse_pattern(date_pattern).type != PatternType.ONE_TIME
