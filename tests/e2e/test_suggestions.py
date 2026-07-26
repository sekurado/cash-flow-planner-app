from __future__ import annotations

from datetime import date

import pytest
from PySide6.QtCore import QThreadPool

from src.domain.entities import EntryType
from tests.e2e.conftest import E2EStack


def _simulation_params(
    *,
    start: date = date(2026, 1, 1),
    end: date = date(2026, 3, 31),
    initial_balance: float = 200.0,
    base_currency: str = "USD",
) -> dict[str, object]:
    return {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "initial_balance": initial_balance,
        "base_currency": base_currency,
    }


@pytest.mark.e2e
def test_deficit_projection_shows_suggestions(
    qtbot: object,
    e2e_stack: E2EStack,
) -> None:
    plan_vm = e2e_stack.plan_vm
    entries_vm = e2e_stack.entries_vm
    simulation_vm = e2e_stack.simulation_vm
    suggestions_vm = e2e_stack.suggestions_vm

    plan_vm.createPlan("Deficit", "USD", 200.0)
    plan_id = plan_vm.plans[0]["id"]
    plan_vm.selectPlan(plan_id)

    entries_vm.createEntry(
        {
            "plan_id": plan_id,
            "entry_type": EntryType.INCOME.value,
            "name": "Salary",
            "date_pattern": "1..",
            "amount": 500.0,
            "currency": "USD",
        }
    )
    entries_vm.createEntry(
        {
            "plan_id": plan_id,
            "entry_type": EntryType.EXPENSE.value,
            "name": "Rent",
            "date_pattern": "5..",
            "amount": 900.0,
            "currency": "USD",
        }
    )

    simulation_vm.runSimulation(plan_id, _simulation_params())
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass
    QThreadPool.globalInstance().waitForDone(5000)
    with qtbot.waitSignal(suggestions_vm.hasSuggestionsChanged, timeout=5000):  # type: ignore[attr-defined]
        pass

    assert suggestions_vm.hasSuggestions is True
    first = suggestions_vm.suggestionAt(0)
    assert first is not None
    assert first["title"]
