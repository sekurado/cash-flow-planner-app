from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from sqlalchemy.engine import Connection

from src.data.repositories.expense_dictionary_repo import (
    SqliteExpenseCategoryRepository,
    SqliteExpenseNameRepository,
    SqliteExpensePlaceRepository,
)
from src.data.repositories.recorded_expense_repo import SqliteRecordedExpenseRepository
from src.domain.receipt_image_store import ReceiptImageStore
from src.domain.recorded_expenses import RecordedExpenseCreate, RecordedExpenseService


@pytest.mark.integration
def test_delete_expense_removes_receipt_image_file(
    db_conn: Connection,
    tmp_path: Path,
    expense_name_repository: SqliteExpenseNameRepository,
    expense_category_repository: SqliteExpenseCategoryRepository,
    expense_place_repository: SqliteExpensePlaceRepository,
    recorded_expense_repository: SqliteRecordedExpenseRepository,
) -> None:
    receipt_store = ReceiptImageStore(tmp_path / "appdata")
    service = RecordedExpenseService(
        recorded_expense_repository,
        expense_name_repository,
        expense_category_repository,
        expense_place_repository,
        receipt_image_store=receipt_store,
    )
    created = service.create(
        RecordedExpenseCreate(
            amount=12.5,
            currency="USD",
            name="Coffee",
            occurred_on=date(2026, 8, 1),
        )
    )
    db_conn.commit()

    source = tmp_path / "receipt.jpg"
    source.write_bytes(b"fake-jpeg")
    updated = service.attach_receipt_image(created.id, source)
    db_conn.commit()

    receipt_path = receipt_store.resolve_path(updated.receipt_image_path or "")
    assert receipt_path.is_file()

    service.delete(created.id)
    db_conn.commit()

    assert recorded_expense_repository.find_by_id(created.id) is None
    assert not receipt_path.exists()
