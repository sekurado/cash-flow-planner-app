from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy.engine import Connection

from src.app.viewmodels.expense_analytics_view_model import ExpenseAnalyticsViewModel
from src.app.viewmodels.recorded_expenses_view_model import RecordedExpensesViewModel
from src.data.repositories.exchange_rate_repo import SqliteExchangeRateRepository
from src.data.repositories.expense_dictionary_repo import (
    SqliteExpenseCategoryRepository,
    SqliteExpenseNameRepository,
    SqliteExpensePlaceRepository,
)
from src.data.repositories.recorded_expense_repo import (
    RecordedExpenseListFilters,
    SqliteRecordedExpenseRepository,
)
from src.domain.recorded_expenses import RecordedExpenseCreate, RecordedExpenseService


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


@pytest.fixture
def expense_analytics_vm(
    recorded_expense_repository: SqliteRecordedExpenseRepository,
    exchange_rate_repository: SqliteExchangeRateRepository,
    recorded_expenses_vm: RecordedExpensesViewModel,
) -> ExpenseAnalyticsViewModel:
    return ExpenseAnalyticsViewModel(
        recorded_expense_repository,
        exchange_rate_repository,
        recorded_expenses_vm,
    )


@pytest.mark.integration
def test_list_filtered_applies_date_range_and_search(
    db_conn: Connection,
    recorded_expense_repository: SqliteRecordedExpenseRepository,
    recorded_expense_service: RecordedExpenseService,
) -> None:
    recorded_expense_service.create(
        _expense_create(
            amount=10.0,
            name="Coffee",
            category="Food",
            place="Cafe",
            occurred_on=date(2026, 3, 5),
            note="Morning latte",
        )
    )
    recorded_expense_service.create(
        _expense_create(
            amount=20.0,
            name="Taxi",
            category="Transport",
            place="Airport",
            occurred_on=date(2026, 2, 20),
        )
    )
    db_conn.commit()

    items = recorded_expense_repository.list_filtered(
        RecordedExpenseListFilters(
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 31),
            search="latte",
        )
    )

    assert len(items) == 1
    assert items[0].name_label == "Coffee"
    assert items[0].note == "Morning latte"


@pytest.mark.integration
def test_analytics_rollups_refresh_after_create_and_respect_date_range(
    qt_app: object,
    db_conn: Connection,
    recorded_expenses_vm: RecordedExpensesViewModel,
    expense_analytics_vm: ExpenseAnalyticsViewModel,
) -> None:
    expense_analytics_vm.setDateRange("2026-03-01", "2026-03-31")

    assert expense_analytics_vm.error == ""
    assert expense_analytics_vm.totalAmount == pytest.approx(0.0)
    assert expense_analytics_vm.categorySeries == []

    recorded_expenses_vm.createExpense(
        {
            "amount": 12.5,
            "currency": "USD",
            "name": "Coffee",
            "category": "Food",
            "place": "Cafe",
            "occurred_on": "2026-03-10",
        }
    )
    db_conn.commit()

    assert expense_analytics_vm.error == ""
    assert expense_analytics_vm.totalAmount == pytest.approx(12.5)
    assert len(expense_analytics_vm.categorySeries) == 1
    assert expense_analytics_vm.categorySeries[0]["label"] == "Food"
    assert expense_analytics_vm.categorySeries[0]["totalAmount"] == pytest.approx(12.5)

    recorded_expenses_vm.createExpense(
        {
            "amount": 99.0,
            "currency": "USD",
            "name": "Rent",
            "category": "Housing",
            "occurred_on": "2026-02-01",
        }
    )
    db_conn.commit()

    assert expense_analytics_vm.totalAmount == pytest.approx(12.5)
    assert len(expense_analytics_vm.categorySeries) == 1


def _expense_create(
    *,
    amount: float,
    name: str,
    category: str,
    place: str,
    occurred_on: date,
    note: str | None = None,
) -> RecordedExpenseCreate:
    return RecordedExpenseCreate(
        amount=amount,
        currency="USD",
        name=name,
        category=category,
        place=place,
        occurred_on=occurred_on,
        note=note,
    )
