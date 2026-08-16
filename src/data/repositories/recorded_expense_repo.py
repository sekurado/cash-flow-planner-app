from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import delete, func, insert, or_, select, update
from sqlalchemy.engine import Connection, RowMapping
from sqlalchemy.sql import Select

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


class RecordedExpenseListFilters(BaseModel):
    model_config = ConfigDict(frozen=True)

    start_date: date | None = None
    end_date: date | None = None
    search: str | None = None
    limit: int | None = None
    sort_by: Literal["date", "amount"] = "date"
    sort_ascending: bool = False

    @field_validator("search", mode="before")
    @classmethod
    def _empty_search_to_none(cls, value: object) -> object | None:
        if value is None:
            return None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped if stripped else None
        return value


class RecordedExpenseAnalyticsRow(BaseModel):
    amount: float
    currency: str
    occurred_on: date
    name_id: str
    name_label: str
    category_id: str | None = None
    category_label: str | None = None
    place_id: str | None = None
    place_label: str | None = None


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _row_to_recorded_expense(row: RowMapping) -> RecordedExpense:
    data: dict[str, Any] = dict(row)
    if "occurred_on" in data:
        data["occurred_on"] = date.fromisoformat(data["occurred_on"])
    return RecordedExpense.model_validate(data)


def _list_from_join() -> Select[Any]:
    return (
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
    )


def _analytics_from_join() -> Select[Any]:
    return (
        select(
            recorded_expenses.c.amount,
            recorded_expenses.c.currency,
            recorded_expenses.c.occurred_on,
            recorded_expenses.c.name_id,
            expense_names.c.label.label("name_label"),
            recorded_expenses.c.category_id,
            expense_categories.c.label.label("category_label"),
            recorded_expenses.c.place_id,
            expense_places.c.label.label("place_label"),
        )
        .select_from(recorded_expenses)
        .join(expense_names, recorded_expenses.c.name_id == expense_names.c.id)
        .outerjoin(
            expense_categories,
            recorded_expenses.c.category_id == expense_categories.c.id,
        )
        .outerjoin(expense_places, recorded_expenses.c.place_id == expense_places.c.id)
    )


def _apply_list_filters(stmt: Select[Any], filters: RecordedExpenseListFilters) -> Select[Any]:
    if filters.start_date is not None:
        stmt = stmt.where(recorded_expenses.c.occurred_on >= filters.start_date.isoformat())
    if filters.end_date is not None:
        stmt = stmt.where(recorded_expenses.c.occurred_on <= filters.end_date.isoformat())
    if filters.search is not None:
        pattern = f"%{filters.search.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(expense_names.c.label).like(pattern),
                func.lower(expense_categories.c.label).like(pattern),
                func.lower(expense_places.c.label).like(pattern),
                func.lower(recorded_expenses.c.note).like(pattern),
            )
        )
    return stmt


def _apply_sort(stmt: Select[Any], filters: RecordedExpenseListFilters) -> Select[Any]:
    if filters.sort_by == "amount":
        primary = recorded_expenses.c.amount
    else:
        primary = recorded_expenses.c.occurred_on
    secondary = recorded_expenses.c.created_at
    if filters.sort_ascending:
        return stmt.order_by(primary.asc(), secondary.asc())
    return stmt.order_by(primary.desc(), secondary.desc())


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
                receipt_image_path=dto.receipt_image_path,
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
                receipt_image_path=dto.receipt_image_path,
                updated_at=now,
            )
        )
        if result.rowcount == 0:
            msg = f"Recorded expense not found: {expense_id}"
            raise ValueError(msg)
        expense = self.find_by_id(expense_id)
        assert expense is not None
        return expense

    def update_receipt_image_path(
        self,
        expense_id: str,
        receipt_image_path: str | None,
    ) -> RecordedExpense:
        now = _utc_now_iso()
        result = self._conn.execute(
            update(recorded_expenses)
            .where(recorded_expenses.c.id == expense_id)
            .values(
                receipt_image_path=receipt_image_path,
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
        return self.list_filtered(RecordedExpenseListFilters(limit=limit))

    def list_filtered(
        self, filters: RecordedExpenseListFilters
    ) -> Sequence[RecordedExpenseListItem]:
        stmt = _apply_sort(_apply_list_filters(_list_from_join(), filters), filters)
        if filters.limit is not None:
            stmt = stmt.limit(filters.limit)
        rows = self._conn.execute(stmt).mappings().all()
        return [_row_to_list_item(row) for row in rows]

    def list_for_analytics(
        self,
        *,
        start_date: date,
        end_date: date,
        search: str | None = None,
    ) -> Sequence[RecordedExpenseAnalyticsRow]:
        filters = RecordedExpenseListFilters(
            start_date=start_date,
            end_date=end_date,
            search=search,
        )
        stmt = _apply_sort(_apply_list_filters(_analytics_from_join(), filters), filters)
        rows = self._conn.execute(stmt).mappings().all()
        return [_row_to_analytics_row(row) for row in rows]


def _row_to_list_item(row: RowMapping) -> RecordedExpenseListItem:
    data = dict(row)
    data["occurred_on"] = date.fromisoformat(data["occurred_on"])
    return RecordedExpenseListItem.model_validate(data)


def _row_to_analytics_row(row: RowMapping) -> RecordedExpenseAnalyticsRow:
    data = dict(row)
    data["occurred_on"] = date.fromisoformat(data["occurred_on"])
    return RecordedExpenseAnalyticsRow.model_validate(data)
