from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Protocol

from pydantic import BaseModel
from sqlalchemy import insert, select
from sqlalchemy.engine import Connection, RowMapping

from src.data.schema import audit_log
from src.domain.entities import AuditLogEntry


class AuditLogCreateDto(BaseModel):
    plan_id: str
    entity_type: str
    entity_id: str
    action: str
    summary: str


class AbstractAuditLogRepository(Protocol):
    def append(self, dto: AuditLogCreateDto) -> AuditLogEntry: ...

    def list_by_plan(self, plan_id: str, limit: int = 100) -> list[AuditLogEntry]: ...


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _row_to_audit_log_entry(row: RowMapping) -> AuditLogEntry:
    return AuditLogEntry.model_validate(dict(row))


class SqliteAuditLogRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def append(self, dto: AuditLogCreateDto) -> AuditLogEntry:
        entry_id = str(uuid.uuid4())
        timestamp = _utc_now_iso()
        self._conn.execute(
            insert(audit_log).values(
                id=entry_id,
                plan_id=dto.plan_id,
                entity_type=dto.entity_type,
                entity_id=dto.entity_id,
                action=dto.action,
                summary=dto.summary,
                timestamp=timestamp,
            )
        )
        entry = self._find_by_id(entry_id)
        assert entry is not None
        return entry

    def list_by_plan(self, plan_id: str, limit: int = 100) -> list[AuditLogEntry]:
        stmt = (
            select(audit_log)
            .where(audit_log.c.plan_id == plan_id)
            .order_by(audit_log.c.timestamp.desc())
            .limit(limit)
        )
        rows = self._conn.execute(stmt).mappings().all()
        return [_row_to_audit_log_entry(row) for row in rows]

    def _find_by_id(self, entry_id: str) -> AuditLogEntry | None:
        stmt = select(audit_log).where(audit_log.c.id == entry_id)
        row = self._conn.execute(stmt).mappings().one_or_none()
        if row is None:
            return None
        return _row_to_audit_log_entry(row)
