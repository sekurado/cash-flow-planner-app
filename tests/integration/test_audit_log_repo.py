from __future__ import annotations

import time

import pytest
from sqlalchemy.engine import Connection

from src.data.repositories.audit_log_repo import AuditLogCreateDto, SqliteAuditLogRepository
from src.data.repositories.plan_repo import PlanCreateDto, SqlitePlanRepository


@pytest.mark.integration
def test_append_and_list_by_plan(
    db_conn: Connection,
    audit_log_repository: SqliteAuditLogRepository,
) -> None:
    plan_repository = SqlitePlanRepository(db_conn)
    plan = plan_repository.create(PlanCreateDto(name="Audit Plan"))
    db_conn.commit()

    first = audit_log_repository.append(
        AuditLogCreateDto(
            plan_id=plan.id,
            entity_type="plan",
            entity_id=plan.id,
            action="create",
            summary="Created forecast",
        )
    )
    time.sleep(0.01)
    second = audit_log_repository.append(
        AuditLogCreateDto(
            plan_id=plan.id,
            entity_type="entry",
            entity_id="entry-1",
            action="create",
            summary="Added income entry",
        )
    )
    db_conn.commit()

    assert first.id
    assert first.plan_id == plan.id
    assert first.timestamp

    entries = audit_log_repository.list_by_plan(plan.id)
    assert len(entries) == 2
    assert entries[0].id == second.id
    assert entries[1].id == first.id


@pytest.mark.integration
def test_list_by_plan_respects_limit(
    db_conn: Connection,
    audit_log_repository: SqliteAuditLogRepository,
) -> None:
    plan_repository = SqlitePlanRepository(db_conn)
    plan = plan_repository.create(PlanCreateDto(name="Limit Plan"))
    db_conn.commit()

    for index in range(3):
        audit_log_repository.append(
            AuditLogCreateDto(
                plan_id=plan.id,
                entity_type="entry",
                entity_id=f"entry-{index}",
                action="create",
                summary=f"Entry {index}",
            )
        )
        time.sleep(0.01)
    db_conn.commit()

    entries = audit_log_repository.list_by_plan(plan.id, limit=2)
    assert len(entries) == 2
    assert entries[0].entity_id == "entry-2"
    assert entries[1].entity_id == "entry-1"


@pytest.mark.integration
def test_audit_log_cascades_on_plan_delete(
    db_conn: Connection,
    audit_log_repository: SqliteAuditLogRepository,
) -> None:
    plan_repository = SqlitePlanRepository(db_conn)
    plan = plan_repository.create(PlanCreateDto(name="Cascade Plan"))
    audit_log_repository.append(
        AuditLogCreateDto(
            plan_id=plan.id,
            entity_type="plan",
            entity_id=plan.id,
            action="create",
            summary="Created forecast",
        )
    )
    db_conn.commit()

    plan_repository.delete(plan.id)
    db_conn.commit()

    assert audit_log_repository.list_by_plan(plan.id) == []
