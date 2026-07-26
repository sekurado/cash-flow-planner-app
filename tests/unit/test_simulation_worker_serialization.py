from __future__ import annotations

from datetime import date

import pytest

from src.app.workers.simulation_worker import (
    deserialize_simulation_result,
    serialize_simulation_result,
)
from src.domain.entities import (
    DailyBalance,
    MonthlySnapshot,
    SimulationParams,
    SimulationResult,
)


def _sample_result() -> SimulationResult:
    return SimulationResult(
        plan_id="plan-1",
        params=SimulationParams(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 5),
            initial_balance=500.0,
            base_currency="USD",
        ),
        daily_balances=(
            DailyBalance(
                date=date(2026, 1, 1),
                events=(),
                day_income=0.0,
                day_expense=0.0,
                closing_balance=500.0,
            ),
            DailyBalance(
                date=date(2026, 1, 2),
                events=(),
                day_income=100.0,
                day_expense=0.0,
                closing_balance=600.0,
            ),
        ),
        monthly_snapshots=(
            MonthlySnapshot(
                year=2026,
                month=1,
                total_income=100.0,
                total_expense=0.0,
                net_flow=100.0,
                closing_balance=600.0,
                deficit=False,
            ),
        ),
        first_deficit_date=None,
        first_deficit_event=None,
        final_balance=600.0,
        total_income=100.0,
        total_expense=0.0,
    )


@pytest.mark.unit
def test_serialize_deserialize_round_trip_preserves_daily_balances() -> None:
    result = _sample_result()

    restored = deserialize_simulation_result(serialize_simulation_result(result))

    assert len(restored.daily_balances) == 2
    assert restored.daily_balances[0].date == date(2026, 1, 1)
    assert restored.daily_balances[0].closing_balance == 500.0
    assert restored.daily_balances[1].day_income == 100.0
    assert restored.daily_balances[1].closing_balance == 600.0


@pytest.mark.unit
def test_deserialize_omits_invalid_daily_balance_rows() -> None:
    payload = serialize_simulation_result(_sample_result())
    payload["daily_balances"] = [
        {"date": "2026-01-01", "day_income": 0.0, "day_expense": 0.0, "closing_balance": 500.0},
        {"date": "bad-date", "day_income": 0.0, "day_expense": 0.0, "closing_balance": 100.0},
        "not-a-dict",
    ]

    restored = deserialize_simulation_result(payload)

    assert len(restored.daily_balances) == 1
    assert restored.daily_balances[0].closing_balance == 500.0
