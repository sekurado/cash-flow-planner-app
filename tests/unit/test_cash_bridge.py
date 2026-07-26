from __future__ import annotations

from datetime import date

import pytest

from src.domain.entities import (
    EntryType,
    MonthlySnapshot,
    NormalizedEvent,
    SimulationParams,
    SimulationResult,
)
from src.domain.simulation_engine import SimulationEngine
from src.export.cash_bridge import build_cash_bridge

_BASE_CURRENCY = "USD"


def _event(
    *,
    event_date: date,
    amount: float,
    entry_type: EntryType = EntryType.INCOME,
    entry_id: str = "entry-1",
) -> NormalizedEvent:
    return NormalizedEvent(
        entry_id=entry_id,
        entry_name="Test",
        date=event_date,
        type=entry_type,
        normalized_amount=amount,
        base_currency=_BASE_CURRENCY,
    )


def _params(
    *,
    start: date,
    end: date,
    initial_balance: float = 1000.0,
) -> SimulationParams:
    return SimulationParams(
        start_date=start,
        end_date=end,
        initial_balance=initial_balance,
        base_currency=_BASE_CURRENCY,
    )


@pytest.mark.unit
def test_single_month_no_events() -> None:
    params = _params(start=date(2026, 1, 1), end=date(2026, 1, 31), initial_balance=500.0)
    result = SimulationEngine.run([], params)

    bridge = build_cash_bridge(result)

    assert len(bridge) == 1
    row = bridge[0]
    assert row.year == 2026
    assert row.month == 1
    assert row.opening_balance == 500.0
    assert row.total_inflows == 0.0
    assert row.total_outflows == 0.0
    assert row.net_flow == 0.0
    assert row.closing_balance == 500.0


@pytest.mark.unit
def test_multi_month_opening_equals_prior_closing() -> None:
    params = _params(start=date(2026, 1, 1), end=date(2026, 3, 31), initial_balance=0.0)
    events = [
        _event(event_date=date(2026, 1, 15), amount=3000.0, entry_id="salary-jan"),
        _event(
            event_date=date(2026, 1, 20),
            amount=500.0,
            entry_type=EntryType.EXPENSE,
            entry_id="rent-jan",
        ),
        _event(event_date=date(2026, 2, 15), amount=3000.0, entry_id="salary-feb"),
        _event(
            event_date=date(2026, 2, 20),
            amount=600.0,
            entry_type=EntryType.EXPENSE,
            entry_id="rent-feb",
        ),
        _event(event_date=date(2026, 3, 15), amount=3000.0, entry_id="salary-mar"),
        _event(
            event_date=date(2026, 3, 20),
            amount=700.0,
            entry_type=EntryType.EXPENSE,
            entry_id="rent-mar",
        ),
    ]
    result = SimulationEngine.run(events, params)

    bridge = build_cash_bridge(result)

    assert len(bridge) == 3
    assert bridge[0].opening_balance == 0.0
    assert bridge[0].closing_balance == 2500.0
    assert bridge[1].opening_balance == bridge[0].closing_balance
    assert bridge[1].closing_balance == 4900.0
    assert bridge[2].opening_balance == bridge[1].closing_balance
    assert bridge[2].closing_balance == 7200.0

    for row in bridge:
        assert row.total_inflows - row.total_outflows == row.net_flow
        assert row.opening_balance + row.net_flow == row.closing_balance


@pytest.mark.unit
def test_empty_monthly_snapshots_returns_empty_tuple() -> None:
    result = SimulationResult(
        plan_id="plan-1",
        params=_params(start=date(2026, 1, 1), end=date(2026, 1, 1)),
        daily_balances=(),
        monthly_snapshots=(),
        first_deficit_date=None,
        first_deficit_event=None,
        final_balance=1000.0,
        total_income=0.0,
        total_expense=0.0,
    )

    assert build_cash_bridge(result) == ()


@pytest.mark.unit
def test_cross_check_raises_on_inconsistent_snapshot() -> None:
    result = SimulationResult(
        plan_id="plan-1",
        params=_params(start=date(2026, 1, 1), end=date(2026, 1, 31), initial_balance=100.0),
        daily_balances=(),
        monthly_snapshots=(
            MonthlySnapshot(
                year=2026,
                month=1,
                total_income=50.0,
                total_expense=10.0,
                net_flow=40.0,
                closing_balance=999.0,
                deficit=False,
            ),
        ),
        first_deficit_date=None,
        first_deficit_event=None,
        final_balance=999.0,
        total_income=50.0,
        total_expense=10.0,
    )

    with pytest.raises(ValueError, match="opening"):
        build_cash_bridge(result)
