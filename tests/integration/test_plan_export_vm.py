from __future__ import annotations

import json
from pathlib import Path

import pytest
from sqlalchemy.engine import Connection

from src.app.viewmodels.plan_vm import PlanViewModel
from src.data.repositories.entry_repo import EntryCreateDto, SqliteEntryRepository
from src.data.repositories.exchange_rate_repo import (
    ExchangeRateUpsertDto,
    SqliteExchangeRateRepository,
)
from src.data.repositories.plan_repo import PlanCreateDto, SqlitePlanRepository
from src.domain.entities import EntryType, PlanExportBundle
from src.export.plan_exporter import PlanExporter


@pytest.fixture
def plan_exporter(db_conn: Connection) -> PlanExporter:
    return PlanExporter(
        SqlitePlanRepository(db_conn),
        SqliteEntryRepository(db_conn),
        SqliteExchangeRateRepository(db_conn),
    )


def _create_exportable_plan(
    db_conn: Connection,
) -> str:
    plan_repo = SqlitePlanRepository(db_conn)
    entry_repo = SqliteEntryRepository(db_conn)
    rate_repo = SqliteExchangeRateRepository(db_conn)
    plan = plan_repo.create(
        PlanCreateDto(name="Household Budget", base_currency="USD", initial_balance=5000.0)
    )
    entry_repo.create(
        EntryCreateDto(
            plan_id=plan.id,
            entry_type=EntryType.INCOME,
            name="Salary",
            date_pattern="10..",
            amount=3000.0,
            currency="USD",
        )
    )
    entry_repo.create(
        EntryCreateDto(
            plan_id=plan.id,
            entry_type=EntryType.EXPENSE,
            name="Rent",
            date_pattern="1..",
            amount=1200.0,
            currency="EUR",
            category="Housing",
            is_active=False,
        )
    )
    rate_repo.upsert(
        ExchangeRateUpsertDto(
            from_currency="EUR",
            to_currency="USD",
            rate=1.08,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )
    return plan.id


@pytest.mark.integration
def test_export_plan_writes_ftplan_and_emits_success(
    qtbot: object,
    plan_repository: SqlitePlanRepository,
    plan_exporter: PlanExporter,
    db_conn: Connection,
    tmp_path: Path,
) -> None:
    plan_id = _create_exportable_plan(db_conn)
    vm = PlanViewModel(plan_repository, plan_exporter)
    output = tmp_path / "budget.ftplan"

    vm.exportPlan(plan_id, str(output))

    with qtbot.waitSignal(vm.exportSucceeded, timeout=5000):  # type: ignore[attr-defined]
        pass

    assert vm.error == ""
    assert output.is_file()
    bundle = PlanExportBundle.model_validate(json.loads(output.read_text(encoding="utf-8")))
    assert bundle.plan.name == "Household Budget"
    assert len(bundle.entries) == 2


@pytest.mark.integration
def test_export_plan_missing_plan_sets_error(
    qtbot: object,
    plan_repository: SqlitePlanRepository,
    plan_exporter: PlanExporter,
    tmp_path: Path,
) -> None:
    vm = PlanViewModel(plan_repository, plan_exporter)
    output = tmp_path / "missing.ftplan"

    vm.exportPlan("nonexistent-plan-id", str(output))

    with qtbot.waitSignal(vm.errorChanged, timeout=5000):  # type: ignore[attr-defined]
        pass

    assert vm.error != ""
    assert not output.exists()
