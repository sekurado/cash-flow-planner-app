from __future__ import annotations

from datetime import date

import pytest

from src.domain.entities import EntryType
from src.domain.exceptions import CurrencyConversionError
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
def test_multi_currency_simulation_normalizes_income_to_base_currency(
    qtbot: object,
    e2e_stack: E2EStack,
) -> None:
    """EUR income with a defined EUR→USD rate is normalised in monthly snapshots."""
    plan_vm = e2e_stack.plan_vm
    entries_vm = e2e_stack.entries_vm
    simulation_vm = e2e_stack.simulation_vm
    currency_vm = e2e_stack.currency_vm

    plan_vm.createPlan("Multi-currency", "USD", 0.0)
    plan_id = plan_vm.plans[0]["id"]
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
    currency_vm.createRate("EUR", "USD", 1.1)

    params = _simulation_params(
        start=_PLAN_START,
        end=_ONE_MONTH_END,
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
    assert snapshot_model.rowCount() == 1
    first_index = snapshot_model.index(0, 0)
    total_income = snapshot_model.data(first_index, snapshot_model.TOTAL_INCOME_ROLE)
    assert total_income == pytest.approx(1100.0)


@pytest.mark.e2e
def test_multi_currency_simulation_missing_rate_surfaces_conversion_error(
    qtbot: object,
    e2e_stack: E2EStack,
) -> None:
    """GBP income without an exchange rate sets simulationViewModel.error."""
    plan_vm = e2e_stack.plan_vm
    entries_vm = e2e_stack.entries_vm
    simulation_vm = e2e_stack.simulation_vm

    plan_vm.createPlan("Missing rate", "USD", 0.0)
    plan_id = plan_vm.plans[0]["id"]
    plan_vm.selectPlan(plan_id)

    entries_vm.createEntry(
        {
            "plan_id": plan_id,
            "entry_type": EntryType.INCOME.value,
            "name": "GBP Salary",
            "date_pattern": "1..",
            "amount": 1000.0,
            "currency": "GBP",
        }
    )

    params = _simulation_params(
        start=_PLAN_START,
        end=_ONE_MONTH_END,
        initial_balance=0.0,
        base_currency="USD",
    )
    simulation_vm.runSimulation(plan_id, params)
    with qtbot.waitSignal(simulation_vm.errorChanged, timeout=5000) as blocker:  # type: ignore[attr-defined]
        pass

    message = blocker.args[0] if blocker.args else simulation_vm.error
    assert message != ""
    assert "GBP → USD" in message or CurrencyConversionError.__name__ in message
    assert simulation_vm.isRunning is False
    assert simulation_vm.result is None
