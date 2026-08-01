from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, date, datetime
from typing import Any

from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.engine import Connection, RowMapping

from src.data.schema import (
    expense_categories,
    expense_names,
    expense_places,
    recorded_expenses,
)
from src.domain.recorded_expenses import RecordedExpense, RecordedExpensePersistDto


class RecordedExpenseListItem(BaseModel):
    id: str
    amount: float
    currency: str
    occurred_on: date
    name_label: str
    category_label: str | None = None
    place_label: str | None = None
    note: str | None = None


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _row_to_recorded_expense(row: RowMapping) -> RecordedExpense:
    data: dict[str, Any] = dict(row)
    if "occurred_on" in data:
        data["occurred_on"] = date.fromisoformat(data["occurred_on"])
    return RecordedExpense.model_validate(data)


class SqliteRecordedExpenseRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def find_by_id(self, expense_id: str) -> RecordedExpense | None:
        stmt = select(recorded_expenses).where(recorded_expenses.c.id == expense_id)
        row = self._conn.execute(stmt).mappings().one_or_none()
        if row is None:
            return None
        return _row_to_recorded_expense(row)

    def create(self, dto: RecordedExpensePersistDto) -> RecordedExpense:
        now = _utc_now_iso()
        expense_id = str(uuid.uuid4())
        self._conn.execute(
            insert(recorded_expenses).values(
                id=expense_id,
                amount=dto.amount,
                currency=dto.currency,
                occurred_on=dto.occurred_on.isoformat(),
                name_id=dto.name_id,
                category_id=dto.category_id,
                place_id=dto.place_id,
                note=dto.note,
                created_at=now,
                updated_at=now,
            )
        )
        expense = self.find_by_id(expense_id)
        assert expense is not None
        return expense

    def update(self, expense_id: str, dto: RecordedExpensePersistDto) -> RecordedExpense:
        now = _utc_now_iso()
        result = self._conn.execute(
            update(recorded_expenses)
            .where(recorded_expenses.c.id == expense_id)
            .values(
                amount=dto.amount,
                currency=dto.currency,
                occurred_on=dto.occurred_on.isoformat(),
                name_id=dto.name_id,
                category_id=dto.category_id,
                place_id=dto.place_id,
                note=dto.note,
                updated_at=now,
            )
        )
        if result.rowcount == 0:
            msg = f"Recorded expense not found: {expense_id}"
            raise ValueError(msg)
        expense = self.find_by_id(expense_id)
        assert expense is not None
        return expense

    def delete(self, expense_id: str) -> None:
        self._conn.execute(delete(recorded_expenses).where(recorded_expenses.c.id == expense_id))

    def list_recent(self, limit: int) -> Sequence[RecordedExpenseListItem]:
        stmt = (
            select(
                recorded_expenses.c.id,
                recorded_expenses.c.amount,
                recorded_expenses.c.currency,
                recorded_expenses.c.occurred_on,
                recorded_expenses.c.note,
                expense_names.c.label.label("name_label"),
                expense_categories.c.label.label("category_label"),
                expense_places.c.label.label("place_label"),
            )
            .select_from(recorded_expenses)
            .join(expense_names, recorded_expenses.c.name_id == expense_names.c.id)
            .outerjoin(
                expense_categories,
                recorded_expenses.c.category_id == expense_categories.c.id,
            )
            .outerjoin(expense_places, recorded_expenses.c.place_id == expense_places.c.id)
            .order_by(
                recorded_expenses.c.occurred_on.desc(),
                recorded_expenses.c.created_at.desc(),
            )
            .limit(limit)
        )
        rows = self._conn.execute(stmt).mappings().all()
        return [_row_to_list_item(row) for row in rows]


def _row_to_list_item(row: RowMapping) -> RecordedExpenseListItem:
    data = dict(row)
    data["occurred_on"] = date.fromisoformat(data["occurred_on"])
    return RecordedExpenseListItem.model_validate(data)
