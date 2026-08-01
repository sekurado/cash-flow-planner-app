from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import cast

from sqlalchemy import Table, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Connection

from src.data.schema import expense_categories, expense_names, expense_places
from src.domain.recorded_expenses import (
    ExpenseCategory,
    ExpenseName,
    ExpensePlace,
    normalize_dictionary_label,
)


def _get_or_create_label[T: ExpenseName | ExpenseCategory | ExpensePlace](
    conn: Connection,
    table: Table,
    label: str,
    row_to_entity: type[T],
) -> T:
    display_label = label.strip()
    normalized_label = normalize_dictionary_label(label)
    stmt = sqlite_insert(table).values(
        id=str(uuid.uuid4()),
        label=display_label,
        normalized_label=normalized_label,
    )
    stmt = stmt.on_conflict_do_nothing(index_elements=["normalized_label"])
    conn.execute(stmt)
    row = (
        conn.execute(select(table).where(table.c.normalized_label == normalized_label))
        .mappings()
        .one()
    )
    return cast(T, row_to_entity.model_validate(dict(row)))


def _search_labels[T: ExpenseName | ExpenseCategory | ExpensePlace](
    conn: Connection,
    table: Table,
    prefix: str,
    limit: int,
    row_to_entity: type[T],
) -> list[T]:
    stripped = prefix.strip()
    if not stripped:
        return []
    normalized_prefix = normalize_dictionary_label(stripped)
    stmt = (
        select(table)
        .where(table.c.normalized_label.like(f"{normalized_prefix}%"))
        .order_by(table.c.label.collate("NOCASE").asc())
        .limit(limit)
    )
    rows = conn.execute(stmt).mappings().all()
    return [cast(T, row_to_entity.model_validate(dict(row))) for row in rows]


class SqliteExpenseNameRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def get_or_create(self, label: str) -> ExpenseName:
        return _get_or_create_label(self._conn, expense_names, label, ExpenseName)

    def search(self, prefix: str, limit: int) -> Sequence[ExpenseName]:
        return _search_labels(self._conn, expense_names, prefix, limit, ExpenseName)


class SqliteExpenseCategoryRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def get_or_create(self, label: str) -> ExpenseCategory:
        return _get_or_create_label(self._conn, expense_categories, label, ExpenseCategory)

    def search(self, prefix: str, limit: int) -> Sequence[ExpenseCategory]:
        return _search_labels(self._conn, expense_categories, prefix, limit, ExpenseCategory)


class SqliteExpensePlaceRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def get_or_create(self, label: str) -> ExpensePlace:
        return _get_or_create_label(self._conn, expense_places, label, ExpensePlace)

    def search(self, prefix: str, limit: int) -> Sequence[ExpensePlace]:
        return _search_labels(self._conn, expense_places, prefix, limit, ExpensePlace)
