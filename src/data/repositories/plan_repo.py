from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Protocol

from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.engine import Connection, RowMapping

from src.data.repositories.audit_log_repo import AbstractAuditLogRepository, AuditLogCreateDto
from src.data.schema import plans
from src.domain.entities import Plan
from src.domain.exceptions import DuplicatePlanNameError


class PlanCreateDto(BaseModel):
    name: str
    base_currency: str = "USD"
    initial_balance: float = 0.0


class PlanUpdateDto(BaseModel):
    name: str | None = None
    base_currency: str | None = None
    initial_balance: float | None = None


class AbstractPlanRepository(Protocol):
    def find_all(self) -> list[Plan]: ...

    def find_by_id(self, plan_id: str) -> Plan | None: ...

    def find_by_name(self, name: str) -> Plan | None: ...

    def create(self, dto: PlanCreateDto) -> Plan: ...

    def update(self, plan_id: str, dto: PlanUpdateDto) -> Plan: ...

    def delete(self, plan_id: str) -> None: ...


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _row_to_plan(row: RowMapping) -> Plan:
    return Plan.model_validate(dict(row))


def _plan_update_summary(existing: Plan, changes: dict[str, object]) -> str:
    parts: list[str] = []
    if "name" in changes:
        parts.append(f"Renamed forecast to '{changes['name']}'")
    if "initial_balance" in changes:
        parts.append(f"Updated opening balance to {changes['initial_balance']}")
    if "base_currency" in changes:
        parts.append(f"Updated base currency to {changes['base_currency']}")
    if parts:
        return "; ".join(parts)
    return f"Updated forecast '{existing.name}'"


class SqlitePlanRepository:
    def __init__(
        self,
        conn: Connection,
        audit_log_repo: AbstractAuditLogRepository | None = None,
    ) -> None:
        self._conn = conn
        self._audit_log_repo = audit_log_repo

    def find_all(self) -> list[Plan]:
        stmt = select(plans).order_by(plans.c.created_at.asc())
        rows = self._conn.execute(stmt).mappings().all()
        return [_row_to_plan(row) for row in rows]

    def find_by_id(self, plan_id: str) -> Plan | None:
        stmt = select(plans).where(plans.c.id == plan_id)
        row = self._conn.execute(stmt).mappings().one_or_none()
        if row is None:
            return None
        return _row_to_plan(row)

    def find_by_name(self, name: str) -> Plan | None:
        stmt = select(plans).where(plans.c.name == name)
        row = self._conn.execute(stmt).mappings().one_or_none()
        if row is None:
            return None
        return _row_to_plan(row)

    def create(self, dto: PlanCreateDto) -> Plan:
        now = _utc_now_iso()
        plan_id = str(uuid.uuid4())
        self._conn.execute(
            insert(plans).values(
                id=plan_id,
                name=dto.name,
                base_currency=dto.base_currency,
                initial_balance=dto.initial_balance,
                created_at=now,
                updated_at=now,
            )
        )
        plan = self.find_by_id(plan_id)
        assert plan is not None
        self._append_audit(
            plan_id=plan.id,
            entity_id=plan.id,
            action="create",
            summary=f"Created forecast '{plan.name}'",
        )
        return plan

    def update(self, plan_id: str, dto: PlanUpdateDto) -> Plan:
        changes = dto.model_dump(exclude_unset=True)
        if not changes:
            existing = self.find_by_id(plan_id)
            if existing is None:
                msg = f"Plan not found: {plan_id}"
                raise ValueError(msg)
            return existing

        existing = self.find_by_id(plan_id)
        if existing is None:
            msg = f"Plan not found: {plan_id}"
            raise ValueError(msg)

        if "name" in changes:
            conflict = self.find_by_name(changes["name"])
            if conflict is not None and conflict.id != plan_id:
                msg = f"Plan name already exists: {changes['name']}"
                raise DuplicatePlanNameError(msg)

        changes["updated_at"] = _utc_now_iso()
        result = self._conn.execute(update(plans).where(plans.c.id == plan_id).values(**changes))
        if result.rowcount == 0:
            msg = f"Plan not found: {plan_id}"
            raise ValueError(msg)
        updated = self.find_by_id(plan_id)
        assert updated is not None
        self._append_audit(
            plan_id=updated.id,
            entity_id=updated.id,
            action="update",
            summary=_plan_update_summary(existing, changes),
        )
        return updated

    def delete(self, plan_id: str) -> None:
        existing = self.find_by_id(plan_id)
        if existing is not None:
            self._append_audit(
                plan_id=existing.id,
                entity_id=existing.id,
                action="delete",
                summary=f"Deleted forecast '{existing.name}'",
            )
        self._conn.execute(delete(plans).where(plans.c.id == plan_id))

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
                entity_type="plan",
                entity_id=entity_id,
                action=action,
                summary=summary,
            )
        )
