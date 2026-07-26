from __future__ import annotations

import time

import pytest
from PySide6.QtCore import QSettings, QTranslator
from PySide6.QtWidgets import QApplication

from src.app.viewmodels.audit_log_vm import AuditLogViewModel
from src.data.repositories.audit_log_repo import AuditLogCreateDto, SqliteAuditLogRepository
from src.data.repositories.plan_repo import PlanCreateDto, SqlitePlanRepository
from src.domain.entities import AuditLogEntry


class FailingAuditLogRepository:
    def append(self, dto: AuditLogCreateDto) -> AuditLogEntry:
        msg = "append not supported in test double"
        raise RuntimeError(msg)

    def list_by_plan(self, plan_id: str, limit: int = 100) -> list[AuditLogEntry]:
        msg = "Audit log unavailable"
        raise RuntimeError(msg)


@pytest.mark.integration
def test_load_for_plan_returns_entries_newest_first(
    qt_app: object,
    plan_repository: SqlitePlanRepository,
    audit_log_repository: SqliteAuditLogRepository,
) -> None:
    plan = plan_repository.create(PlanCreateDto(name="History Plan"))
    create_records = audit_log_repository.list_by_plan(plan.id)
    assert len(create_records) == 1

    time.sleep(0.01)
    second = audit_log_repository.append(
        AuditLogCreateDto(
            plan_id=plan.id,
            entity_type="entry",
            entity_id="entry-1",
            action="create",
            summary="Added cash flow 'Rent'",
        )
    )

    vm = AuditLogViewModel(audit_log_repository)
    vm.loadForPlan(plan.id)

    assert vm.error == ""
    assert len(vm.entries) == 2
    assert vm.entries[0]["id"] == second.id
    assert vm.entries[0]["summary"] == "Added cash flow 'Rent'"
    assert vm.entries[1]["id"] == create_records[0].id
    assert vm.entries[1]["timestamp"]


@pytest.mark.integration
def test_load_for_plan_sets_error_without_raising(
    qt_app: object,
) -> None:
    vm = AuditLogViewModel(FailingAuditLogRepository())

    vm.loadForPlan("missing-plan")

    assert vm.error != ""
    assert vm.entries == []


@pytest.mark.integration
def test_retranslate_updates_loaded_summaries(
    qt_app: QApplication,
    plan_repository: SqlitePlanRepository,
    audit_log_repository: SqliteAuditLogRepository,
) -> None:
    import src.app.resources_rc  # noqa: F401

    plan = plan_repository.create(PlanCreateDto(name="Localized History"))
    vm = AuditLogViewModel(audit_log_repository)
    vm.loadForPlan(plan.id)

    assert vm.entries[0]["summary"] == "Created forecast 'Localized History'"

    translator = QTranslator()
    assert translator.load(":/i18n/app_ru.qm")
    qt_app.installTranslator(translator)
    QSettings().setValue("language", "ru")

    try:
        vm.retranslate()
        assert vm.entries[0]["summary"] == "Создан прогноз «Localized History»"
    finally:
        QSettings().setValue("language", "en")
        qt_app.removeTranslator(translator)


@pytest.mark.integration
def test_clear_error_clears_message(
    qt_app: object,
) -> None:
    vm = AuditLogViewModel(FailingAuditLogRepository())
    vm.loadForPlan("missing-plan")
    assert vm.error != ""

    vm.clearError()

    assert vm.error == ""
