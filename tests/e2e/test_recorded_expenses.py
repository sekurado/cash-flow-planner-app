from __future__ import annotations

import pytest

from tests.e2e.conftest import E2EStack


@pytest.mark.e2e
def test_add_recorded_expense_persists_in_list(
    qtbot: object,
    e2e_stack: E2EStack,
) -> None:
    """Create a recorded expense through the ViewModel and verify it appears in the list."""
    recorded_expenses_vm = e2e_stack.recorded_expenses_vm
    list_model = recorded_expenses_vm.expenseListModel

    recorded_expenses_vm.loadExpenses()
    assert list_model.rowCount() == 0

    with qtbot.waitSignal(recorded_expenses_vm.expenseCreated, timeout=5000):  # type: ignore[attr-defined]
        recorded_expenses_vm.createExpense(
            {
                "amount": 24.99,
                "currency": "USD",
                "name": "Groceries",
                "category": "Food",
                "place": "Whole Foods",
            }
        )

    assert recorded_expenses_vm.error == ""
    assert list_model.rowCount() == 1

    index = list_model.index(0, 0)
    assert list_model.data(index, list_model.NAME_LABEL_ROLE) == "Groceries"
    assert list_model.data(index, list_model.AMOUNT_ROLE) == 24.99
    assert list_model.data(index, list_model.CURRENCY_ROLE) == "USD"
    assert list_model.data(index, list_model.CATEGORY_LABEL_ROLE) == "Food"
    assert list_model.data(index, list_model.PLACE_LABEL_ROLE) == "Whole Foods"
