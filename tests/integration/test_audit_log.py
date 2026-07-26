from __future__ import annotations

from dataclasses import dataclass, field

import pytest
from sqlalchemy.engine import Connection

from src.data.repositories.audit_log_repo import (
    AuditLogCreateDto,
    SqliteAuditLogRepository,
)
from src.data.repositories.entry_repo import EntryCreateDto, EntryUpdateDto, SqliteEntryRepository
from src.data.repositories.plan_repo import PlanCreateDto, PlanUpdateDto, SqlitePlanRepository
from src.domain.entities import AuditLogEntry, EntryType


@dataclass
class RecordingAuditLogRepository:
    inner: SqliteAuditLogRepository
    calls: list[AuditLogCreateDto] = field(default_factory=list)

    def append(self, dto: AuditLogCreateDto) -> AuditLogEntry:
        self.calls.append(dto)
        return self.inner.append(dto)

    def list_by_plan(self, plan_id: str, limit: int = 100) -> list[AuditLogEntry]:
        return self.inner.list_by_plan(plan_id, limit=limit)


@pytest.mark.integration
def test_plan_create_writes_audit_record(
    db_conn: Connection,
    plan_repository: SqlitePlanRepository,
    audit_log_repository: SqliteAuditLogRepository,
) -> None:
    plan = plan_repository.create(PlanCreateDto(name="Q1 Runway"))
    db_conn.commit()

    entries = audit_log_repository.list_by_plan(plan.id)
    assert len(entries) == 1
    record = entries[0]
    assert record.plan_id == plan.id
    assert record.entity_type == "plan"
    assert record.entity_id == plan.id
    assert record.action == "create"
    assert record.summary == "Created forecast 'Q1 Runway'"
    assert record.timestamp


@pytest.mark.integration
def test_plan_update_writes_audit_record(
    db_conn: Connection,
    plan_repository: SqlitePlanRepository,
    audit_log_repository: SqliteAuditLogRepository,
) -> None:
    plan = plan_repository.create(PlanCreateDto(name="Draft", initial_balance=10000.0))
    db_conn.commit()

    plan_repository.update(
        plan.id,
        PlanUpdateDto(name="Q1 Runway (revised)", initial_balance=25000.0),
    )
    db_conn.commit()

    entries = audit_log_repository.list_by_plan(plan.id)
    assert len(entries) == 2
    update_record = entries[0]
    assert update_record.action == "update"
    assert update_record.summary == (
        "Renamed forecast to 'Q1 Runway (revised)'; Updated opening balance to 25000.0"
    )


@pytest.mark.integration
def test_plan_delete_writes_audit_record_before_cascade(
    db_conn: Connection,
    audit_log_repository: SqliteAuditLogRepository,
) -> None:
    recording_repo = RecordingAuditLogRepository(audit_log_repository)
    plan_repository = SqlitePlanRepository(db_conn, recording_repo)
    plan = plan_repository.create(PlanCreateDto(name="Old draft"))
    db_conn.commit()

    plan_repository.delete(plan.id)
    db_conn.commit()

    delete_calls = [call for call in recording_repo.calls if call.action == "delete"]
    assert len(delete_calls) == 1
    assert delete_calls[0].summary == "Deleted forecast 'Old draft'"
    assert audit_log_repository.list_by_plan(plan.id) == []


@pytest.mark.integration
def test_entry_create_writes_audit_record_with_plan_fk(
    db_conn: Connection,
    plan_repository: SqlitePlanRepository,
    entry_repository: SqliteEntryRepository,
    audit_log_repository: SqliteAuditLogRepository,
) -> None:
    plan = plan_repository.create(PlanCreateDto(name="Office Plan"))
    db_conn.commit()

    entry = entry_repository.create(
        EntryCreateDto(
            plan_id=plan.id,
            entry_type=EntryType.EXPENSE,
            name="Office rent",
            date_pattern="monthly on 1",
            amount=2000.0,
            currency="USD",
        )
    )
    db_conn.commit()

    entries = audit_log_repository.list_by_plan(plan.id)
    entry_records = [record for record in entries if record.entity_type == "entry"]
    assert len(entry_records) == 1
    record = entry_records[0]
    assert record.plan_id == plan.id
    assert record.entity_id == entry.id
    assert record.action == "create"
    assert record.summary == "Added cash flow 'Office rent' (expense)"


@pytest.mark.integration
def test_entry_update_writes_audit_record(
    db_conn: Connection,
    plan_repository: SqlitePlanRepository,
    entry_repository: SqliteEntryRepository,
    audit_log_repository: SqliteAuditLogRepository,
) -> None:
    plan = plan_repository.create(PlanCreateDto(name="Office Plan"))
    entry = entry_repository.create(
        EntryCreateDto(
            plan_id=plan.id,
            entry_type=EntryType.EXPENSE,
            name="Office rent",
            date_pattern="monthly on 1",
            amount=2000.0,
            currency="USD",
        )
    )
    db_conn.commit()

    entry_repository.update(entry.id, EntryUpdateDto(amount=2200.0))
    db_conn.commit()

    entries = audit_log_repository.list_by_plan(plan.id)
    update_records = [
        record for record in entries if record.entity_type == "entry" and record.action == "update"
    ]
    assert len(update_records) == 1
    assert update_records[0].summary == "Updated cash flow 'Office rent': amount 2000.0 → 2200.0"


@pytest.mark.integration
def test_entry_delete_writes_audit_record(
    db_conn: Connection,
    plan_repository: SqlitePlanRepository,
    entry_repository: SqliteEntryRepository,
    audit_log_repository: SqliteAuditLogRepository,
) -> None:
    plan = plan_repository.create(PlanCreateDto(name="Office Plan"))
    entry = entry_repository.create(
        EntryCreateDto(
            plan_id=plan.id,
            entry_type=EntryType.EXPENSE,
            name="Office rent",
            date_pattern="monthly on 1",
            amount=2000.0,
            currency="USD",
        )
    )
    db_conn.commit()

    entry_repository.delete(entry.id)
    db_conn.commit()

    entries = audit_log_repository.list_by_plan(plan.id)
    delete_records = [
        record for record in entries if record.entity_type == "entry" and record.action == "delete"
    ]
    assert len(delete_records) == 1
    assert delete_records[0].summary == "Removed cash flow 'Office rent'"
