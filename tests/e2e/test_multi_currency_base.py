from __future__ import annotations

from datetime import date

import pytest

from src.domain.entities import EntryType
from tests.e2e.conftest import E2EStack

_PLAN_START = date(2026, 1, 1)
_ONE_MONTH_END = date(2026, 1, 31)


def _simulation_params(
    *,
    start: date,
    end: date,
    initial_balance: float,
    base_currency: str,
) -> dict[str, object]:
    return {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "initial_balance": initial_balance,
        "base_currency": base_currency,
    }


@pytest.mark.e2e
def test_eur_base_plan_simulation_normalizes_foreign_entries(
    qtbot: object,
    e2e_stack: E2EStack,
) -> None:
    """EUR-base plan normalises EUR and USD entries using a USD → EUR rate."""
    plan_vm = e2e_stack.plan_vm
    entries_vm = e2e_stack.entries_vm
    simulation_vm = e2e_stack.simulation_vm
    currency_vm = e2e_stack.currency_vm

    plan_vm.createPlan("EUR Budget", "EUR", 1000.0)
    plan = plan_vm.plans[0]
    plan_id = plan["id"]
    assert plan["base_currency"] == "EUR"
    plan_vm.selectPlan(plan_id)

    entries_vm.createEntry(
        {
            "plan_id": plan_id,
            "entry_type": EntryType.INCOME.value,
            "name": "EUR Salary",
            "date_pattern": "1..",
            "amount": 1000.0,
            "currency": "EUR",
        }
    )
    entries_vm.createEntry(
        {
            "plan_id": plan_id,
            "entry_type": EntryType.INCOME.value,
            "name": "USD Bonus",
            "date_pattern": "1..",
            "amount": 1000.0,
            "currency": "USD",
        }
    )
    currency_vm.createRate("USD", "EUR", 0.9)

    params = _simulation_params(
        start=_PLAN_START,
        end=_ONE_MONTH_END,
        initial_balance=1000.0,
        base_currency="EUR",
    )
    simulation_vm.runSimulation(plan_id, params)
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass

    assert simulation_vm.error == ""
    result = simulation_vm.result
    assert result is not None
    assert result["first_deficit_date"] is None

    snapshot_model = simulation_vm.snapshotModel
    assert snapshot_model.rowCount() == 1
    first_index = snapshot_model.index(0, 0)
    total_income = snapshot_model.data(first_index, snapshot_model.TOTAL_INCOME_ROLE)
    closing_balance = snapshot_model.data(first_index, snapshot_model.CLOSING_BALANCE_ROLE)
    assert total_income == pytest.approx(1900.0)
    assert closing_balance == pytest.approx(2900.0)
