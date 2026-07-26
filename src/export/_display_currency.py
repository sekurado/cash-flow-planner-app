from __future__ import annotations

from src.domain.currency_normalizer import convert_amount
from src.domain.entities import ExchangeRate, MonthlySnapshot, SimulationResult


def _convert_money(
    amount: float,
    source_currency: str,
    display_currency: str,
    exchange_rates: list[ExchangeRate],
) -> float:
    if display_currency == source_currency:
        return amount
    return convert_amount(amount, source_currency, display_currency, exchange_rates)


def convert_snapshot(
    snapshot: MonthlySnapshot,
    source_currency: str,
    display_currency: str,
    exchange_rates: list[ExchangeRate],
) -> MonthlySnapshot:
    if display_currency == source_currency:
        return snapshot
    return MonthlySnapshot(
        year=snapshot.year,
        month=snapshot.month,
        total_income=_convert_money(
            snapshot.total_income, source_currency, display_currency, exchange_rates
        ),
        total_expense=_convert_money(
            snapshot.total_expense, source_currency, display_currency, exchange_rates
        ),
        net_flow=_convert_money(
            snapshot.net_flow, source_currency, display_currency, exchange_rates
        ),
        closing_balance=_convert_money(
            snapshot.closing_balance, source_currency, display_currency, exchange_rates
        ),
        deficit=snapshot.deficit,
    )


def convert_result_for_display(
    result: SimulationResult,
    display_currency: str,
    exchange_rates: list[ExchangeRate],
) -> SimulationResult:
    source_currency = result.params.base_currency
    if display_currency == source_currency:
        return result
    return SimulationResult(
        plan_id=result.plan_id,
        params=result.params,
        daily_balances=result.daily_balances,
        monthly_snapshots=tuple(
            convert_snapshot(snapshot, source_currency, display_currency, exchange_rates)
            for snapshot in result.monthly_snapshots
        ),
        first_deficit_date=result.first_deficit_date,
        first_deficit_event=result.first_deficit_event,
        final_balance=_convert_money(
            result.final_balance, source_currency, display_currency, exchange_rates
        ),
        total_income=_convert_money(
            result.total_income, source_currency, display_currency, exchange_rates
        ),
        total_expense=_convert_money(
            result.total_expense, source_currency, display_currency, exchange_rates
        ),
    )
