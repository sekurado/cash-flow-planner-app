from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, Protocol

from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.engine import Connection, RowMapping

from src.data.repositories.audit_log_repo import AbstractAuditLogRepository, AuditLogCreateDto
from src.data.schema import entries
from src.domain.entities import Entry, EntryCreateDTO, EntryType


class EntryCreateDto(BaseModel):
    plan_id: str
    entry_type: EntryType
    name: str
    date_pattern: str
    amount: float
    currency: str
    category: str | None = None
    is_active: bool = True


class EntryUpdateDto(BaseModel):
    entry_type: EntryType | None = None
    name: str | None = None
    date_pattern: str | None = None
    amount: float | None = None
    currency: str | None = None
    category: str | None = None
    is_active: bool | None = None


class AbstractEntryRepository(Protocol):
    def find_by_plan_id(self, plan_id: str) -> list[Entry]: ...

    def find_by_id(self, entry_id: str) -> Entry | None: ...

    def create(self, dto: EntryCreateDto) -> Entry: ...

    def create_many(self, plan_id: str, entries: Sequence[EntryCreateDTO]) -> list[Entry]: ...

    def update(self, entry_id: str, dto: EntryUpdateDto) -> Entry: ...

    def delete(self, entry_id: str) -> None: ...


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _row_to_entry(row: RowMapping) -> Entry:
    data: dict[str, Any] = dict(row)
    if "is_active" in data:
        data["is_active"] = bool(data["is_active"])
    return Entry.model_validate(data)


def _entry_type_label(entry_type: EntryType | str) -> str:
    value = entry_type.value if isinstance(entry_type, EntryType) else entry_type
    return value


def _entry_update_summary(existing: Entry, changes: dict[str, object]) -> str:
    name = str(changes.get("name", existing.name))
    parts: list[str] = []
    if "amount" in changes:
        parts.append(f"amount {existing.amount} → {changes['amount']}")
    if "name" in changes:
        parts.append(f"renamed to '{changes['name']}'")
    if "entry_type" in changes:
        entry_type = changes["entry_type"]
        label = entry_type.value if isinstance(entry_type, EntryType) else str(entry_type)
        parts.append(f"type {existing.entry_type.value} → {label}")
    if "currency" in changes:
        parts.append(f"currency {existing.currency} → {changes['currency']}")
    if "date_pattern" in changes:
        parts.append("schedule updated")
    if "category" in changes:
        parts.append("category updated")
    if "is_active" in changes:
        state = "active" if changes["is_active"] else "inactive"
        parts.append(f"marked {state}")
    if parts:
        return f"Updated cash flow '{name}': {'; '.join(parts)}"
    return f"Updated cash flow '{name}'"


class SqliteEntryRepository:
    def __init__(
        self,
        conn: Connection,
        audit_log_repo: AbstractAuditLogRepository | None = None,
    ) -> None:
        self._conn = conn
        self._audit_log_repo = audit_log_repo

    def find_by_plan_id(self, plan_id: str) -> list[Entry]:
        stmt = (
            select(entries).where(entries.c.plan_id == plan_id).order_by(entries.c.created_at.asc())
        )
        rows = self._conn.execute(stmt).mappings().all()
        return [_row_to_entry(row) for row in rows]

    def find_by_id(self, entry_id: str) -> Entry | None:
        stmt = select(entries).where(entries.c.id == entry_id)
        row = self._conn.execute(stmt).mappings().one_or_none()
        if row is None:
            return None
        return _row_to_entry(row)

    def create(self, dto: EntryCreateDto) -> Entry:
        now = _utc_now_iso()
        entry_id = str(uuid.uuid4())
        self._conn.execute(
            insert(entries).values(
                id=entry_id,
                plan_id=dto.plan_id,
                entry_type=dto.entry_type.value,
                name=dto.name,
                date_pattern=dto.date_pattern,
                amount=dto.amount,
                currency=dto.currency,
                category=dto.category,
                is_active=dto.is_active,
                created_at=now,
            )
        )
        entry = self.find_by_id(entry_id)
        assert entry is not None
        self._append_audit(
            plan_id=entry.plan_id,
            entity_id=entry.id,
            action="create",
            summary=(f"Added cash flow '{entry.name}' ({_entry_type_label(entry.entry_type)})"),
        )
        return entry

    def create_many(self, plan_id: str, entry_dtos: Sequence[EntryCreateDTO]) -> list[Entry]:
        if not entry_dtos:
            return []

        now = _utc_now_iso()
        values: list[dict[str, Any]] = []
        entry_ids: list[str] = []
        for entry_dto in entry_dtos:
            entry_id = str(uuid.uuid4())
            entry_ids.append(entry_id)
            values.append(
                {
                    "id": entry_id,
                    "plan_id": plan_id,
                    "entry_type": entry_dto.entry_type.value,
                    "name": entry_dto.name,
                    "date_pattern": entry_dto.date_pattern,
                    "amount": entry_dto.amount,
                    "currency": entry_dto.currency,
                    "category": entry_dto.category,
                    "is_active": entry_dto.is_active,
                    "created_at": now,
                }
            )

        self._conn.execute(insert(entries), values)
        stmt = select(entries).where(entries.c.id.in_(entry_ids))
        rows = self._conn.execute(stmt).mappings().all()
        by_id: dict[str, Entry] = {}
        for row in rows:
            loaded_entry = _row_to_entry(row)
            by_id[loaded_entry.id] = loaded_entry
        created = [by_id[entry_id] for entry_id in entry_ids]
        for created_entry in created:
            self._append_audit(
                plan_id=created_entry.plan_id,
                entity_id=created_entry.id,
                action="create",
                summary=(
                    f"Added cash flow '{created_entry.name}' "
                    f"({_entry_type_label(created_entry.entry_type)})"
                ),
            )
        return created

    def update(self, entry_id: str, dto: EntryUpdateDto) -> Entry:
        changes = dto.model_dump(exclude_unset=True)
        if not changes:
            existing = self.find_by_id(entry_id)
            if existing is None:
                msg = f"Entry not found: {entry_id}"
                raise ValueError(msg)
            return existing

        existing = self.find_by_id(entry_id)
        if existing is None:
            msg = f"Entry not found: {entry_id}"
            raise ValueError(msg)

        if "entry_type" in changes:
            entry_type = changes["entry_type"]
            changes["entry_type"] = (
                entry_type.value if isinstance(entry_type, EntryType) else entry_type
            )

        result = self._conn.execute(
            update(entries).where(entries.c.id == entry_id).values(**changes)
        )
        if result.rowcount == 0:
            msg = f"Entry not found: {entry_id}"
            raise ValueError(msg)
        updated = self.find_by_id(entry_id)
        assert updated is not None
        self._append_audit(
            plan_id=updated.plan_id,
            entity_id=updated.id,
            action="update",
            summary=_entry_update_summary(existing, changes),
        )
        return updated

    def delete(self, entry_id: str) -> None:
        existing = self.find_by_id(entry_id)
        if existing is not None:
            self._append_audit(
                plan_id=existing.plan_id,
                entity_id=existing.id,
                action="delete",
                summary=f"Removed cash flow '{existing.name}'",
            )
        self._conn.execute(delete(entries).where(entries.c.id == entry_id))

    def _append_audit(
        self,
        *,
        plan_id: str,
        entity_id: str,
        action: str,
        summary: str,
    ) -> None:
        if self._audit_log_repo is None:
            return
        self._audit_log_repo.append(
            AuditLogCreateDto(
                plan_id=plan_id,
                entity_type="entry",
                entity_id=entity_id,
                action=action,
                summary=summary,
            )
        )
