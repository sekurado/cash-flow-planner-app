from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy.engine import Connection

from src.data.repositories.expense_dictionary_repo import (
    SqliteExpenseCategoryRepository,
    SqliteExpenseNameRepository,
    SqliteExpensePlaceRepository,
)
from src.data.repositories.recorded_expense_repo import SqliteRecordedExpenseRepository
from src.domain.recorded_expenses import RecordedExpenseCreate, RecordedExpenseService


@pytest.mark.integration
def test_expense_name_get_or_create_deduplicates_case_insensitive(
    db_conn: Connection,
    expense_name_repository: SqliteExpenseNameRepository,
) -> None:
    first = expense_name_repository.get_or_create("Netflix")
    second = expense_name_repository.get_or_create("  netflix  ")
    db_conn.commit()

    assert first.id == second.id
    assert first.label == "Netflix"


@pytest.mark.integration
def test_expense_name_search_prefix_case_insensitive(
    db_conn: Connection,
    expense_name_repository: SqliteExpenseNameRepository,
) -> None:
    expense_name_repository.get_or_create("Netflix")
    expense_name_repository.get_or_create("Netgear")
    expense_name_repository.get_or_create("Spotify")
    db_conn.commit()

    matches = expense_name_repository.search("net", limit=10)

    assert [match.label for match in matches] == ["Netflix", "Netgear"]


@pytest.mark.integration
def test_recorded_expense_service_round_trip(
    db_conn: Connection,
    expense_name_repository: SqliteExpenseNameRepository,
    expense_category_repository: SqliteExpenseCategoryRepository,
    expense_place_repository: SqliteExpensePlaceRepository,
    recorded_expense_repository: SqliteRecordedExpenseRepository,
) -> None:
    service = RecordedExpenseService(
        recorded_expense_repository,
        expense_name_repository,
        expense_category_repository,
        expense_place_repository,
    )
    created = service.create(
        RecordedExpenseCreate(
            amount=12.5,
            currency="usd",
            name="Coffee",
            category="Food",
            place="Cafe Nero",
            occurred_on=date(2026, 7, 15),
            note="Morning latte",
        )
    )
    db_conn.commit()

    loaded = recorded_expense_repository.find_by_id(created.id)
    assert loaded is not None
    assert loaded.amount == 12.5
    assert loaded.currency == "USD"
    assert loaded.occurred_on == date(2026, 7, 15)
    assert loaded.note == "Morning latte"

    items = recorded_expense_repository.list_recent(limit=10)
    assert len(items) == 1
    assert items[0].name_label == "Coffee"
    assert items[0].category_label == "Food"
    assert items[0].place_label == "Cafe Nero"

    updated = service.update(
        created.id,
        RecordedExpenseCreate(
            amount=15.0,
            currency="USD",
            name="Coffee",
            category="Food",
            place="Cafe Nero",
            occurred_on=date(2026, 7, 16),
        ),
    )
    db_conn.commit()

    assert updated.amount == 15.0
    assert updated.occurred_on == date(2026, 7, 16)

    service.delete(created.id)
    db_conn.commit()

    assert recorded_expense_repository.find_by_id(created.id) is None
