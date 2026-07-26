from __future__ import annotations

from datetime import date

import pytest

from src.app.viewmodels.simulation_vm import SimulationViewModel
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


def _deficit_banner_visible(simulation_vm: SimulationViewModel) -> bool:
    """Mirror DeficitBanner.qml visibility (hasDeficit with userDismissed=false)."""
    result = simulation_vm.result
    if result is None:
        return False
    first_deficit_date = result.get("first_deficit_date")
    return first_deficit_date is not None


@pytest.mark.e2e
def test_deficit_detection_expense_exceeds_balance(
    qtbot: object,
    e2e_stack: E2EStack,
) -> None:
    """Monthly expense with zero balance triggers deficit detection and banner visibility."""
    plan_vm = e2e_stack.plan_vm
    entries_vm = e2e_stack.entries_vm
    simulation_vm = e2e_stack.simulation_vm

    plan_vm.createPlan("Test", "USD", 0.0)
    plan_id = plan_vm.plans[0]["id"]
    plan_vm.selectPlan(plan_id)

    entries_vm.createEntry(
        {
            "plan_id": plan_id,
            "entry_type": EntryType.EXPENSE.value,
            "name": "Bills",
            "date_pattern": "1..",
            "amount": 500.0,
            "currency": "USD",
        }
    )

    params = _simulation_params(
        start=date(2026, 1, 1),
        end=date(2026, 2, 28),
        initial_balance=0.0,
        base_currency="USD",
    )
    simulation_vm.runSimulation(plan_id, params)
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass

    assert simulation_vm.error == ""
    result = simulation_vm.result
    assert result is not None
    assert result["first_deficit_date"] is not None
    assert _deficit_banner_visible(simulation_vm) is True
