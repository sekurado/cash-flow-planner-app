from __future__ import annotations

from datetime import date

import pytest

from src.domain.entities import EntryType
from tests.e2e.conftest import E2EStack


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
def test_happy_path_income_exceeds_expense_no_deficit(
    qtbot: object,
    e2e_stack: E2EStack,
) -> None:
    """Create plan, add income/expense entries, run simulation — no deficit expected."""
    plan_vm = e2e_stack.plan_vm
    entries_vm = e2e_stack.entries_vm
    simulation_vm = e2e_stack.simulation_vm

    plan_vm.createPlan("Test", "USD", 0.0)
    plan_id = plan_vm.plans[0]["id"]
    plan_vm.selectPlan(plan_id)

    entries_vm.createEntry(
        {
            "plan_id": plan_id,
            "entry_type": EntryType.INCOME.value,
            "name": "Salary",
            "date_pattern": "1..",
            "amount": 2000.0,
            "currency": "USD",
        }
    )
    entries_vm.createEntry(
        {
            "plan_id": plan_id,
            "entry_type": EntryType.EXPENSE.value,
            "name": "Rent",
            "date_pattern": "15..",
            "amount": 1500.0,
            "currency": "USD",
        }
    )

    params = _simulation_params(
        start=date(2026, 1, 1),
        end=date(2026, 3, 31),
        initial_balance=0.0,
        base_currency="USD",
    )
    simulation_vm.runSimulation(plan_id, params)
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass

    assert simulation_vm.error == ""
    result = simulation_vm.result
    assert result is not None
    assert result["first_deficit_date"] is None

    snapshot_model = simulation_vm.snapshotModel
    assert snapshot_model.rowCount() >= 1
    first_index = snapshot_model.index(0, 0)
    total_income = snapshot_model.data(first_index, snapshot_model.TOTAL_INCOME_ROLE)
    assert total_income == 2000.0
