from __future__ import annotations

import json
from pathlib import Path

import pytest
from sqlalchemy.engine import Connection

from src.app.identity import LEGACY_PYPROJECT_NAME
from src.app.viewmodels.plan_import_vm import PlanImportViewModel
from src.data.repositories.entry_repo import SqliteEntryRepository
from src.data.repositories.exchange_rate_repo import (
    ExchangeRateUpsertDto,
    SqliteExchangeRateRepository,
)
from src.data.repositories.plan_repo import SqlitePlanRepository
from src.integrations.plan_import_service import PlanImportService


def _sample_bundle_payload() -> dict[str, object]:
    return {
        "format_version": 1,
        "app": LEGACY_PYPROJECT_NAME,
        "exported_at": "2026-06-27T12:00:00Z",
        "plan": {
            "name": "Household Budget",
            "base_currency": "USD",
            "initial_balance": 5000.0,
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
            },
            {
                "entry_type": "expense",
                "name": "Rent",
                "date_pattern": "1..",
                "amount": 1200.0,
                "currency": "EUR",
                "category": "Housing",
                "is_active": False,
            },
        ],
        "exchange_rates": [
            {"from_currency": "EUR", "to_currency": "USD", "rate": 1.15},
            {"from_currency": "JPY", "to_currency": "USD", "rate": 0.0067},
        ],
    }


def _write_bundle(path: Path, payload: dict[str, object] | None = None) -> None:
    path.write_text(json.dumps(payload or _sample_bundle_payload(), indent=2), encoding="utf-8")


@pytest.fixture
def plan_import_vm(db_conn: Connection) -> PlanImportViewModel:
    service = PlanImportService(
        SqlitePlanRepository(db_conn),
        SqliteEntryRepository(db_conn),
        SqliteExchangeRateRepository(db_conn),
        db_conn,
    )
    return PlanImportViewModel(service)


@pytest.mark.integration
def test_inspect_file_populates_preview_properties(
    plan_import_vm: PlanImportViewModel,
    tmp_path: Path,
) -> None:
    bundle_path = tmp_path / "budget.ftplan"
    _write_bundle(bundle_path)

    plan_import_vm.inspectFile(str(bundle_path))

    assert plan_import_vm.error == ""
    assert plan_import_vm.previewName == "Household Budget"
    assert plan_import_vm.previewEntryCount == 2
    assert plan_import_vm.previewCurrencies == ["EUR", "USD"]
    assert len(plan_import_vm.rateAdditions) == 2
    assert plan_import_vm.hasRateConflicts is False


@pytest.mark.integration
def test_inspect_file_classifies_rate_conflicts(
    plan_import_vm: PlanImportViewModel,
    exchange_rate_repository: SqliteExchangeRateRepository,
    tmp_path: Path,
) -> None:
    exchange_rate_repository.upsert(
        ExchangeRateUpsertDto(
            from_currency="EUR",
            to_currency="USD",
            rate=1.08,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )
    bundle_path = tmp_path / "conflict.ftplan"
    _write_bundle(bundle_path)

    plan_import_vm.inspectFile(str(bundle_path))

    assert plan_import_vm.hasRateConflicts is True
    assert len(plan_import_vm.rateConflicts) == 1
    conflict = plan_import_vm.rateConflicts[0]
    assert conflict["fromCurrency"] == "EUR"
    assert conflict["localRate"] == 1.08
    assert conflict["fileRate"] == 1.15
    assert conflict["resolution"] == "keep"


@pytest.mark.integration
def test_set_rate_resolution_updates_conflicts(
    qtbot: object,
    plan_import_vm: PlanImportViewModel,
    exchange_rate_repository: SqliteExchangeRateRepository,
    tmp_path: Path,
) -> None:
    exchange_rate_repository.upsert(
        ExchangeRateUpsertDto(
            from_currency="EUR",
            to_currency="USD",
            rate=1.08,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )
    bundle_path = tmp_path / "conflict.ftplan"
    _write_bundle(bundle_path)
    plan_import_vm.inspectFile(str(bundle_path))

    with qtbot.waitSignal(plan_import_vm.rateConflictsChanged, timeout=5000):  # type: ignore[attr-defined]
        plan_import_vm.setRateResolution("EUR", "use_file")

    assert plan_import_vm.rateConflicts[0]["resolution"] == "use_file"


@pytest.mark.integration
def test_set_all_rate_resolutions_updates_every_conflict(
    qtbot: object,
    plan_import_vm: PlanImportViewModel,
    exchange_rate_repository: SqliteExchangeRateRepository,
    tmp_path: Path,
) -> None:
    exchange_rate_repository.upsert(
        ExchangeRateUpsertDto(
            from_currency="EUR",
            to_currency="USD",
            rate=1.08,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )
    bundle_path = tmp_path / "conflict.ftplan"
    _write_bundle(bundle_path)
    plan_import_vm.inspectFile(str(bundle_path))

    with qtbot.waitSignal(plan_import_vm.rateConflictsChanged, timeout=5000):  # type: ignore[attr-defined]
        plan_import_vm.setAllRateResolutions("use_file")

    assert all(conflict["resolution"] == "use_file" for conflict in plan_import_vm.rateConflicts)


@pytest.mark.integration
def test_import_file_creates_plan_and_emits_completed(
    qtbot: object,
    plan_import_vm: PlanImportViewModel,
    plan_repository: SqlitePlanRepository,
    entry_repository: SqliteEntryRepository,
    tmp_path: Path,
) -> None:
    bundle_path = tmp_path / "budget.ftplan"
    _write_bundle(bundle_path)
    initial_plan_count = len(plan_repository.find_all())

    plan_import_vm.importFile(str(bundle_path))

    with qtbot.waitSignal(plan_import_vm.importCompleted, timeout=5000) as blocker:  # type: ignore[attr-defined]
        pass

    plan_id = blocker.args[0]
    assert plan_import_vm.error == ""
    assert plan_import_vm.isImporting is False
    assert len(plan_repository.find_all()) == initial_plan_count + 1
    assert plan_repository.find_by_id(plan_id) is not None
    assert len(entry_repository.find_by_plan_id(plan_id)) == 2


@pytest.mark.integration
def test_import_file_keep_resolution_leaves_existing_rate_unchanged(
    qtbot: object,
    plan_import_vm: PlanImportViewModel,
    exchange_rate_repository: SqliteExchangeRateRepository,
    tmp_path: Path,
) -> None:
    exchange_rate_repository.upsert(
        ExchangeRateUpsertDto(
            from_currency="EUR",
            to_currency="USD",
            rate=1.08,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )
    bundle_path = tmp_path / "conflict.ftplan"
    _write_bundle(bundle_path)

    plan_import_vm.importFile(str(bundle_path))

    with qtbot.waitSignal(plan_import_vm.importCompleted, timeout=5000):  # type: ignore[attr-defined]
        pass

    rates = {
        (rate.from_currency, rate.to_currency): rate.rate
        for rate in exchange_rate_repository.get_all()
    }
    assert rates[("EUR", "USD")] == 1.08


@pytest.mark.integration
def test_import_file_use_file_resolution_overwrites_existing_rate(
    qtbot: object,
    plan_import_vm: PlanImportViewModel,
    exchange_rate_repository: SqliteExchangeRateRepository,
    tmp_path: Path,
) -> None:
    exchange_rate_repository.upsert(
        ExchangeRateUpsertDto(
            from_currency="EUR",
            to_currency="USD",
            rate=1.08,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )
    bundle_path = tmp_path / "conflict.ftplan"
    _write_bundle(bundle_path)

    plan_import_vm.inspectFile(str(bundle_path))
    plan_import_vm.setRateResolution("EUR", "use_file")
    plan_import_vm.importFile(str(bundle_path))

    with qtbot.waitSignal(plan_import_vm.importCompleted, timeout=5000):  # type: ignore[attr-defined]
        pass

    rates = {
        (rate.from_currency, rate.to_currency): rate.rate
        for rate in exchange_rate_repository.get_all()
    }
    assert rates[("EUR", "USD")] == 1.15


@pytest.mark.integration
def test_import_file_invalid_path_sets_error(
    plan_import_vm: PlanImportViewModel,
) -> None:
    plan_import_vm.importFile(str(Path("/nonexistent/plan.ftplan")))

    assert plan_import_vm.error != ""
    assert plan_import_vm.isImporting is False
