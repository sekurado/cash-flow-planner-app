from __future__ import annotations

import json
import stat
from pathlib import Path

import pytest
from sqlalchemy.engine import Connection

from src.data.repositories.entry_repo import EntryCreateDto, SqliteEntryRepository
from src.data.repositories.exchange_rate_repo import (
    ExchangeRateUpsertDto,
    SqliteExchangeRateRepository,
)
from src.data.repositories.plan_repo import PlanCreateDto, SqlitePlanRepository
from src.domain.entities import EntryType, PlanExportBundle
from src.domain.exceptions import PlanExportError
from src.export.plan_exporter import PlanExporter


@pytest.fixture
def plan_exporter(db_conn: Connection) -> PlanExporter:
    return PlanExporter(
        SqlitePlanRepository(db_conn),
        SqliteEntryRepository(db_conn),
        SqliteExchangeRateRepository(db_conn),
    )


@pytest.fixture
def plan_exporter_repos(
    db_conn: Connection,
) -> tuple[SqlitePlanRepository, SqliteEntryRepository, SqliteExchangeRateRepository]:
    return (
        SqlitePlanRepository(db_conn),
        SqliteEntryRepository(db_conn),
        SqliteExchangeRateRepository(db_conn),
    )


def _create_plan_with_entries(
    repos: tuple[SqlitePlanRepository, SqliteEntryRepository, SqliteExchangeRateRepository],
) -> str:
    plan_repo, entry_repo, rate_repo = repos
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
    rate_repo.upsert(
        ExchangeRateUpsertDto(
            from_currency="GBP",
            to_currency="USD",
            rate=1.25,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )
    return plan.id


@pytest.mark.unit
def test_export_writes_valid_bundle_json(
    plan_exporter: PlanExporter,
    plan_exporter_repos: tuple[
        SqlitePlanRepository, SqliteEntryRepository, SqliteExchangeRateRepository
    ],
    tmp_path: Path,
) -> None:
    plan_id = _create_plan_with_entries(plan_exporter_repos)
    output = tmp_path / "budget.ftplan"

    plan_exporter.export(plan_id, output, app_version="0.1.0")

    bundle = PlanExportBundle.model_validate(json.loads(output.read_text(encoding="utf-8")))
    assert bundle.format_version == 1
    assert bundle.app == "cash-flow-planner-desktop"
    assert bundle.plan.name == "Household Budget"
    assert bundle.plan.base_currency == "USD"
    assert bundle.plan.initial_balance == 5000.0
    assert len(bundle.entries) == 2
    assert bundle.entries[0].name == "Salary"
    assert bundle.entries[1].currency == "EUR"
    assert bundle.entries[1].category == "Housing"
    assert bundle.entries[1].is_active is False
    assert bundle.metadata is not None
    assert bundle.metadata["app_version"] == "0.1.0"
    assert bundle.metadata["methodology_version"] == "1.0"


@pytest.mark.unit
def test_export_includes_only_referenced_rates_for_plan_base(
    plan_exporter: PlanExporter,
    plan_exporter_repos: tuple[
        SqlitePlanRepository, SqliteEntryRepository, SqliteExchangeRateRepository
    ],
    tmp_path: Path,
) -> None:
    plan_id = _create_plan_with_entries(plan_exporter_repos)
    output = tmp_path / "budget.ftplan"

    plan_exporter.export(plan_id, output)

    bundle = PlanExportBundle.model_validate(json.loads(output.read_text(encoding="utf-8")))
    assert len(bundle.exchange_rates) == 1
    assert bundle.exchange_rates[0].from_currency == "EUR"
    assert bundle.exchange_rates[0].to_currency == "USD"
    assert bundle.exchange_rates[0].rate == 1.08


@pytest.mark.unit
def test_export_eur_base_plan_bundles_foreign_to_eur_rates(
    plan_exporter: PlanExporter,
    plan_exporter_repos: tuple[
        SqlitePlanRepository, SqliteEntryRepository, SqliteExchangeRateRepository
    ],
    tmp_path: Path,
) -> None:
    plan_repo, entry_repo, rate_repo = plan_exporter_repos
    plan = plan_repo.create(
        PlanCreateDto(name="Euro Budget", base_currency="EUR", initial_balance=2000.0)
    )
    entry_repo.create(
        EntryCreateDto(
            plan_id=plan.id,
            entry_type=EntryType.EXPENSE,
            name="US Supplier",
            date_pattern="1..",
            amount=500.0,
            currency="USD",
        )
    )
    rate_repo.upsert(
        ExchangeRateUpsertDto(
            from_currency="USD",
            to_currency="EUR",
            rate=0.92,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )

    output = tmp_path / "euro-budget.ftplan"
    plan_exporter.export(plan.id, output)

    bundle = PlanExportBundle.model_validate(json.loads(output.read_text(encoding="utf-8")))
    assert bundle.plan.base_currency == "EUR"
    assert len(bundle.exchange_rates) == 1
    assert bundle.exchange_rates[0].from_currency == "USD"
    assert bundle.exchange_rates[0].to_currency == "EUR"
    assert bundle.exchange_rates[0].rate == 0.92


@pytest.mark.unit
def test_export_omits_rates_when_all_entries_are_usd(
    plan_exporter: PlanExporter,
    plan_exporter_repos: tuple[
        SqlitePlanRepository, SqliteEntryRepository, SqliteExchangeRateRepository
    ],
    tmp_path: Path,
) -> None:
    plan_repo, entry_repo, _ = plan_exporter_repos
    plan = plan_repo.create(
        PlanCreateDto(name="USD Only", base_currency="USD", initial_balance=0.0)
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

    output = tmp_path / "usd-only.ftplan"
    plan_exporter.export(plan.id, output)

    bundle = PlanExportBundle.model_validate(json.loads(output.read_text(encoding="utf-8")))
    assert bundle.exchange_rates == []


@pytest.mark.unit
def test_export_raises_when_plan_not_found(
    plan_exporter: PlanExporter,
    tmp_path: Path,
) -> None:
    with pytest.raises(PlanExportError, match="Plan not found"):
        plan_exporter.export("missing-plan-id", tmp_path / "missing.ftplan")


@pytest.mark.unit
def test_export_raises_when_path_not_writable(
    plan_exporter: PlanExporter,
    plan_exporter_repos: tuple[
        SqlitePlanRepository, SqliteEntryRepository, SqliteExchangeRateRepository
    ],
    tmp_path: Path,
) -> None:
    plan_id = _create_plan_with_entries(plan_exporter_repos)
    read_only_dir = tmp_path / "readonly"
    read_only_dir.mkdir()
    read_only_dir.chmod(stat.S_IREAD | stat.S_IEXEC)

    try:
        with pytest.raises(PlanExportError):
            plan_exporter.export(plan_id, read_only_dir / "budget.ftplan")
    finally:
        read_only_dir.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
