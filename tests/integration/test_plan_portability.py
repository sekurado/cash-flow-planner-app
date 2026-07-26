from __future__ import annotations

import json
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
from src.export.plan_exporter import PlanExporter
from src.integrations.plan_import_service import PlanImportService


@pytest.fixture
def portability_stack(
    db_conn: Connection,
    plan_repository: SqlitePlanRepository,
    entry_repository: SqliteEntryRepository,
    exchange_rate_repository: SqliteExchangeRateRepository,
) -> tuple[PlanExporter, PlanImportService, SqlitePlanRepository, SqliteEntryRepository]:
    exporter = PlanExporter(plan_repository, entry_repository, exchange_rate_repository)
    importer = PlanImportService(
        plan_repository, entry_repository, exchange_rate_repository, db_conn
    )
    return exporter, importer, plan_repository, entry_repository


def _create_source_plan(
    plan_repo: SqlitePlanRepository,
    entry_repo: SqliteEntryRepository,
    rate_repo: SqliteExchangeRateRepository,
) -> str:
    plan = plan_repo.create(
        PlanCreateDto(name="Portable Budget", base_currency="USD", initial_balance=7500.0)
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


def _entry_snapshot(entry: object) -> dict[str, object]:
    return {
        "entry_type": entry.entry_type.value,
        "name": entry.name,
        "date_pattern": entry.date_pattern,
        "amount": entry.amount,
        "currency": entry.currency,
        "category": entry.category,
        "is_active": entry.is_active,
    }


@pytest.mark.integration
def test_export_import_round_trip_preserves_plan_and_entries(
    portability_stack: tuple[
        PlanExporter, PlanImportService, SqlitePlanRepository, SqliteEntryRepository
    ],
    exchange_rate_repository: SqliteExchangeRateRepository,
    tmp_path: Path,
) -> None:
    exporter, importer, plan_repo, entry_repo = portability_stack
    source_plan_id = _create_source_plan(plan_repo, entry_repo, exchange_rate_repository)
    source_plan = plan_repo.find_by_id(source_plan_id)
    assert source_plan is not None
    source_entries = entry_repo.find_by_plan_id(source_plan_id)
    bundle_path = tmp_path / "portable.ftplan"

    exporter.export(source_plan_id, bundle_path)
    imported_plan_id = importer.import_bundle(importer.inspect(bundle_path).bundle, {})

    assert imported_plan_id != source_plan_id

    imported_plan = plan_repo.find_by_id(imported_plan_id)
    assert imported_plan is not None
    assert imported_plan.name == f"{source_plan.name} (imported)"
    assert imported_plan.base_currency == source_plan.base_currency
    assert imported_plan.initial_balance == source_plan.initial_balance

    imported_entries = entry_repo.find_by_plan_id(imported_plan_id)
    assert len(imported_entries) == len(source_entries)
    assert sorted(
        (_entry_snapshot(entry) for entry in imported_entries), key=lambda item: item["name"]
    ) == sorted((_entry_snapshot(entry) for entry in source_entries), key=lambda item: item["name"])


@pytest.mark.integration
def test_export_import_round_trip_appends_suffix_on_name_collision(
    portability_stack: tuple[
        PlanExporter, PlanImportService, SqlitePlanRepository, SqliteEntryRepository
    ],
    exchange_rate_repository: SqliteExchangeRateRepository,
    tmp_path: Path,
) -> None:
    exporter, importer, plan_repo, entry_repo = portability_stack
    source_plan_id = _create_source_plan(plan_repo, entry_repo, exchange_rate_repository)
    bundle_path = tmp_path / "portable.ftplan"
    exporter.export(source_plan_id, bundle_path)

    imported_plan_id = importer.import_bundle(importer.inspect(bundle_path).bundle, {})
    imported_plan = plan_repo.find_by_id(imported_plan_id)
    assert imported_plan is not None
    assert imported_plan.name == "Portable Budget (imported)"

    second_import_id = importer.import_bundle(importer.inspect(bundle_path).bundle, {})
    second_import = plan_repo.find_by_id(second_import_id)
    assert second_import is not None
    assert second_import.name == "Portable Budget (imported) (imported)"


@pytest.mark.integration
def test_export_import_round_trip_preserves_metadata_block(
    portability_stack: tuple[
        PlanExporter, PlanImportService, SqlitePlanRepository, SqliteEntryRepository
    ],
    exchange_rate_repository: SqliteExchangeRateRepository,
    tmp_path: Path,
) -> None:
    exporter, importer, plan_repo, entry_repo = portability_stack
    source_plan_id = _create_source_plan(plan_repo, entry_repo, exchange_rate_repository)
    bundle_path = tmp_path / "with-metadata.ftplan"

    exporter.export(source_plan_id, bundle_path, app_version="1.2.3")

    exported = PlanExportBundle.model_validate(json.loads(bundle_path.read_text(encoding="utf-8")))
    assert exported.metadata is not None
    assert exported.metadata["app_version"] == "1.2.3"
    assert exported.metadata["methodology_version"] == "1.0"
    assert exported.metadata["display_currency"] == "USD"
    assert "fx_rates" in exported.metadata

    imported_plan_id = importer.import_bundle(exported, {})
    imported_plan = plan_repo.find_by_id(imported_plan_id)
    assert imported_plan is not None
    assert len(entry_repo.find_by_plan_id(imported_plan_id)) == 2


@pytest.mark.integration
def test_import_bundle_without_metadata_block_succeeds(
    portability_stack: tuple[
        PlanExporter, PlanImportService, SqlitePlanRepository, SqliteEntryRepository
    ],
    tmp_path: Path,
) -> None:
    _, importer, plan_repo, entry_repo = portability_stack
    legacy_payload = {
        "format_version": 1,
        "app": "financial-tracker-desktop",
        "exported_at": "2026-01-01T00:00:00+00:00",
        "plan": {
            "name": "Legacy Export",
            "base_currency": "USD",
            "initial_balance": 1000.0,
        },
        "entries": [
            {
                "entry_type": "income",
                "name": "Salary",
                "date_pattern": "10..",
                "amount": 3000.0,
                "currency": "USD",
                "category": None,
                "is_active": True,
            }
        ],
        "exchange_rates": [],
    }
    bundle_path = tmp_path / "legacy.ftplan"
    bundle_path.write_text(json.dumps(legacy_payload), encoding="utf-8")

    legacy_bundle = PlanExportBundle.model_validate(
        json.loads(bundle_path.read_text(encoding="utf-8"))
    )
    assert legacy_bundle.metadata is None

    imported_plan_id = importer.import_bundle(legacy_bundle, {})

    imported_plan = plan_repo.find_by_id(imported_plan_id)
    assert imported_plan is not None
    assert imported_plan.name == "Legacy Export"
    assert imported_plan.initial_balance == 1000.0
    assert len(entry_repo.find_by_plan_id(imported_plan_id)) == 1
