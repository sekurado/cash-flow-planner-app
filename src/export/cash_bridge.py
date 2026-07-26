from __future__ import annotations

import math

from src.domain.entities import SimulationResult
from src.export.models import CashBridgeMonth

_MONEY_TOLERANCE = 1e-6


def build_cash_bridge(result: SimulationResult) -> tuple[CashBridgeMonth, ...]:
    """Derive monthly cash-bridge rows from a simulation result.

    Opening balance for the first month is ``params.initial_balance``; each
    subsequent month opens at the prior month's closing balance. Inflows,
    outflows, net flow, and closing balance come from ``monthly_snapshots`` and
    are cross-checked against ``daily_balances``.
    """
    rows: list[CashBridgeMonth] = []
    opening = result.params.initial_balance

    for snapshot in result.monthly_snapshots:
        row = CashBridgeMonth(
            year=snapshot.year,
            month=snapshot.month,
            opening_balance=opening,
            total_inflows=snapshot.total_income,
            total_outflows=snapshot.total_expense,
            net_flow=snapshot.net_flow,
            closing_balance=snapshot.closing_balance,
        )
        _cross_check_row(row, result)
        rows.append(row)
        opening = snapshot.closing_balance

    return tuple(rows)


def _cross_check_row(row: CashBridgeMonth, result: SimulationResult) -> None:
    if not math.isclose(
        row.opening_balance + row.net_flow,
        row.closing_balance,
        abs_tol=_MONEY_TOLERANCE,
    ):
        msg = (
            f"Cash bridge mismatch for {row.year}-{row.month:02d}: "
            f"opening ({row.opening_balance}) + net ({row.net_flow}) "
            f"!= closing ({row.closing_balance})"
        )
        raise ValueError(msg)

    if not math.isclose(
        row.total_inflows - row.total_outflows,
        row.net_flow,
        abs_tol=_MONEY_TOLERANCE,
    ):
        msg = (
            f"Cash bridge net-flow mismatch for {row.year}-{row.month:02d}: "
            f"inflows ({row.total_inflows}) - outflows ({row.total_outflows}) "
            f"!= net ({row.net_flow})"
        )
        raise ValueError(msg)

    month_days = [
        daily
        for daily in result.daily_balances
        if daily.date.year == row.year and daily.date.month == row.month
    ]
    if not month_days:
        return

    last_day_closing = month_days[-1].closing_balance
    if not math.isclose(last_day_closing, row.closing_balance, abs_tol=_MONEY_TOLERANCE):
        msg = (
            f"Cash bridge closing mismatch for {row.year}-{row.month:02d}: "
            f"snapshot ({row.closing_balance}) != last daily balance ({last_day_closing})"
        )
        raise ValueError(msg)

    first_day = month_days[0]
    expected_opening = first_day.closing_balance - first_day.day_income + first_day.day_expense
    if not math.isclose(expected_opening, row.opening_balance, abs_tol=_MONEY_TOLERANCE):
        msg = (
            f"Cash bridge opening mismatch for {row.year}-{row.month:02d}: "
            f"derived ({expected_opening}) != row opening ({row.opening_balance})"
        )
        raise ValueError(msg)
