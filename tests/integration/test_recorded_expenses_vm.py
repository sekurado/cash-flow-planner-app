from __future__ import annotations

import pytest
from sqlalchemy.engine import Connection

from src.app.viewmodels.recorded_expenses_view_model import RecordedExpensesViewModel
from src.data.repositories.expense_dictionary_repo import (
    SqliteExpenseCategoryRepository,
    SqliteExpenseNameRepository,
    SqliteExpensePlaceRepository,
)
from src.data.repositories.recorded_expense_repo import SqliteRecordedExpenseRepository
from src.domain.recorded_expenses import RecordedExpenseService


@pytest.fixture
def recorded_expense_service(
    recorded_expense_repository: SqliteRecordedExpenseRepository,
    expense_name_repository: SqliteExpenseNameRepository,
    expense_category_repository: SqliteExpenseCategoryRepository,
    expense_place_repository: SqliteExpensePlaceRepository,
) -> RecordedExpenseService:
    return RecordedExpenseService(
        recorded_expense_repository,
        expense_name_repository,
        expense_category_repository,
        expense_place_repository,
    )


@pytest.fixture
def recorded_expenses_vm(
    recorded_expense_service: RecordedExpenseService,
    recorded_expense_repository: SqliteRecordedExpenseRepository,
    expense_name_repository: SqliteExpenseNameRepository,
    expense_category_repository: SqliteExpenseCategoryRepository,
    expense_place_repository: SqliteExpensePlaceRepository,
) -> RecordedExpensesViewModel:
    return RecordedExpensesViewModel(
        recorded_expense_service,
        recorded_expense_repository,
        expense_name_repository,
        expense_category_repository,
        expense_place_repository,
        search_limit=10,
    )


def _flush_debounced_searches(qtbot: object) -> None:
    qtbot.wait(350)  # type: ignore[attr-defined]


@pytest.mark.integration
def test_create_expense_increases_row_count(
    qt_app: object,
    db_conn: Connection,
    recorded_expenses_vm: RecordedExpensesViewModel,
) -> None:
    recorded_expenses_vm.loadExpenses()
    assert recorded_expenses_vm.expenseListModel.rowCount() == 0

    recorded_expenses_vm.createExpense(
        {
            "amount": 12.5,
            "currency": "USD",
            "name": "Coffee",
            "category": "Food",
            "place": "Cafe Nero",
            "note": "Morning latte",
        }
    )
    db_conn.commit()

    assert recorded_expenses_vm.error == ""
    assert recorded_expenses_vm.expenseListModel.rowCount() == 1
    assert (
        recorded_expenses_vm.expenseListModel.data(
            recorded_expenses_vm.expenseListModel.index(0, 0),
            recorded_expenses_vm.expenseListModel.NAME_LABEL_ROLE,
        )
        == "Coffee"
    )


@pytest.mark.integration
def test_delete_expense_clears_row_count(
    qt_app: object,
    db_conn: Connection,
    recorded_expenses_vm: RecordedExpensesViewModel,
) -> None:
    recorded_expenses_vm.createExpense(
        {
            "amount": 12.5,
            "currency": "USD",
            "name": "Coffee",
        }
    )
    db_conn.commit()
    expense_id = recorded_expenses_vm.expenseListModel.data(
        recorded_expenses_vm.expenseListModel.index(0, 0),
        recorded_expenses_vm.expenseListModel.EXPENSE_ID_ROLE,
    )
    assert isinstance(expense_id, str)

    recorded_expenses_vm.deleteExpense(expense_id)
    db_conn.commit()

    assert recorded_expenses_vm.error == ""
    assert recorded_expenses_vm.expenseListModel.rowCount() == 0


@pytest.mark.integration
def test_search_expense_names_returns_prefix_matches(
    qtbot: object,
    db_conn: Connection,
    expense_name_repository: SqliteExpenseNameRepository,
    recorded_expenses_vm: RecordedExpensesViewModel,
) -> None:
    expense_name_repository.get_or_create("Netflix")
    expense_name_repository.get_or_create("Netgear")
    expense_name_repository.get_or_create("Spotify")
    db_conn.commit()

    recorded_expenses_vm.searchExpenseNames("net")
    _flush_debounced_searches(qtbot)

    assert recorded_expenses_vm.error == ""
    model = recorded_expenses_vm.nameSuggestionModel
    assert model.rowCount() == 2
    labels = [model.data(model.index(row, 0), model.LABEL_ROLE) for row in range(model.rowCount())]
    assert labels == ["Netflix", "Netgear"]


@pytest.mark.integration
def test_create_expense_invalid_amount_sets_error(
    qt_app: object,
    recorded_expenses_vm: RecordedExpensesViewModel,
) -> None:
    recorded_expenses_vm.createExpense(
        {
            "amount": 0,
            "currency": "USD",
            "name": "Coffee",
        }
    )

    assert recorded_expenses_vm.error != ""
    assert recorded_expenses_vm.expenseListModel.rowCount() == 0
