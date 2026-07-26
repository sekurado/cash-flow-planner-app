from __future__ import annotations

import json
from pathlib import Path

import pytest
from sqlalchemy.engine import Connection

from src.app.identity import LEGACY_PYPROJECT_NAME, PYPROJECT_NAME
from src.data.repositories.entry_repo import SqliteEntryRepository
from src.data.repositories.exchange_rate_repo import (
    ExchangeRateUpsertDto,
    SqliteExchangeRateRepository,
)
from src.data.repositories.plan_repo import PlanCreateDto, SqlitePlanRepository
from src.domain.entities import PlanExportBundle
from src.domain.exceptions import PlanImportError
from src.integrations.plan_import_service import PlanImportService


@pytest.fixture
def import_service(db_conn: Connection) -> PlanImportService:
    return PlanImportService(
        SqlitePlanRepository(db_conn),
        SqliteEntryRepository(db_conn),
        SqliteExchangeRateRepository(db_conn),
        db_conn,
    )


@pytest.fixture
def import_repos(
    db_conn: Connection,
) -> tuple[SqlitePlanRepository, SqliteEntryRepository, SqliteExchangeRateRepository]:
    return (
        SqlitePlanRepository(db_conn),
        SqliteEntryRepository(db_conn),
        SqliteExchangeRateRepository(db_conn),
    )


def _sample_bundle_payload(
    *,
    format_version: int = 1,
    plan_name: str = "Household Budget",
    date_pattern: str = "10..",
) -> dict[str, object]:
    return {
        "format_version": format_version,
        "app": PYPROJECT_NAME,
        "exported_at": "2026-06-27T12:00:00Z",
        "plan": {
            "name": plan_name,
            "base_currency": "USD",
            "initial_balance": 5000.0,
        },
        "entries": [
            {
                "entry_type": "income",
                "name": "Salary",
                "date_pattern": date_pattern,
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


def _write_bundle(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _bundle_from_payload(payload: dict[str, object]) -> PlanExportBundle:
    return PlanExportBundle.model_validate(payload)


@pytest.mark.unit
def test_inspect_accepts_legacy_app_identifier(
    import_service: PlanImportService,
    tmp_path: Path,
) -> None:
    bundle_path = tmp_path / "legacy.ftplan"
    payload = _sample_bundle_payload()
    payload["app"] = LEGACY_PYPROJECT_NAME
    _write_bundle(bundle_path, payload)

    preview = import_service.inspect(bundle_path)

    assert preview.bundle.app == LEGACY_PYPROJECT_NAME


@pytest.mark.unit
def test_inspect_rejects_unknown_app_identifier(
    import_service: PlanImportService,
    tmp_path: Path,
) -> None:
    bundle_path = tmp_path / "unknown.ftplan"
    payload = _sample_bundle_payload()
    payload["app"] = "other-app"
    _write_bundle(bundle_path, payload)

    with pytest.raises(PlanImportError, match="Unsupported app identifier"):
        import_service.inspect(bundle_path)


@pytest.mark.unit
def test_inspect_parses_valid_ftplan_file(
    import_service: PlanImportService,
    tmp_path: Path,
) -> None:
    bundle_path = tmp_path / "budget.ftplan"
    _write_bundle(bundle_path, _sample_bundle_payload())

    preview = import_service.inspect(bundle_path)

    assert preview.bundle.plan.name == "Household Budget"
    assert len(preview.bundle.entries) == 2
    assert {rate.from_currency for rate in preview.rate_additions} == {"EUR", "JPY"}
    assert preview.rate_conflicts == []
    assert preview.rate_unchanged == []


@pytest.mark.unit
def test_inspect_classifies_rate_additions_conflicts_and_unchanged(
    import_service: PlanImportService,
    import_repos: tuple[SqlitePlanRepository, SqliteEntryRepository, SqliteExchangeRateRepository],
    tmp_path: Path,
) -> None:
    _, _, rate_repo = import_repos
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

    payload = _sample_bundle_payload()
    payload["exchange_rates"] = [
        {"from_currency": "EUR", "to_currency": "USD", "rate": 1.15},
        {"from_currency": "GBP", "to_currency": "USD", "rate": 1.25},
        {"from_currency": "JPY", "to_currency": "USD", "rate": 0.0067},
    ]
    bundle_path = tmp_path / "rates.ftplan"
    _write_bundle(bundle_path, payload)

    preview = import_service.inspect(bundle_path)

    assert len(preview.rate_additions) == 1
    assert preview.rate_additions[0].from_currency == "JPY"
    assert len(preview.rate_conflicts) == 1
    assert preview.rate_conflicts[0].from_currency == "EUR"
    assert preview.rate_conflicts[0].local_rate == 1.08
    assert preview.rate_conflicts[0].file_rate == 1.15
    assert len(preview.rate_unchanged) == 1
    assert preview.rate_unchanged[0].from_currency == "GBP"


@pytest.mark.unit
def test_inspect_raises_for_malformed_json(
    import_service: PlanImportService,
    tmp_path: Path,
) -> None:
    bad_path = tmp_path / "bad.ftplan"
    bad_path.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(PlanImportError, match="Invalid JSON"):
        import_service.inspect(bad_path)


@pytest.mark.unit
def test_inspect_raises_for_unsupported_format_version(
    import_service: PlanImportService,
    tmp_path: Path,
) -> None:
    bundle_path = tmp_path / "future.ftplan"
    _write_bundle(bundle_path, _sample_bundle_payload(format_version=99))

    with pytest.raises(PlanImportError, match="Unsupported format version"):
        import_service.inspect(bundle_path)


@pytest.mark.unit
def test_import_bundle_creates_plan_with_bundled_base_currency(
    import_service: PlanImportService,
    import_repos: tuple[SqlitePlanRepository, SqliteEntryRepository, SqliteExchangeRateRepository],
) -> None:
    plan_repo, _, _ = import_repos
    payload = _sample_bundle_payload()
    payload["plan"]["base_currency"] = "GBP"
    payload["exchange_rates"] = [
        {"from_currency": "EUR", "to_currency": "GBP", "rate": 0.86},
    ]
    bundle = _bundle_from_payload(payload)

    plan_id = import_service.import_bundle(bundle, {})

    created = plan_repo.find_by_id(plan_id)
    assert created is not None
    assert created.base_currency == "GBP"


@pytest.mark.unit
def test_import_bundle_creates_plan_and_entries(
    import_service: PlanImportService,
    import_repos: tuple[SqlitePlanRepository, SqliteEntryRepository, SqliteExchangeRateRepository],
) -> None:
    plan_repo, entry_repo, _ = import_repos
    bundle = _bundle_from_payload(_sample_bundle_payload())

    plan_id = import_service.import_bundle(bundle, {})

    created = plan_repo.find_by_id(plan_id)
    assert created is not None
    assert created.name == "Household Budget"
    assert created.base_currency == "USD"
    assert created.initial_balance == 5000.0

    entries = entry_repo.find_by_plan_id(plan_id)
    assert len(entries) == 2
    assert entries[0].name == "Salary"
    assert entries[1].currency == "EUR"
    assert entries[1].is_active is False


@pytest.mark.unit
def test_import_bundle_appends_imported_suffix_on_name_collision(
    import_service: PlanImportService,
    import_repos: tuple[SqlitePlanRepository, SqliteEntryRepository, SqliteExchangeRateRepository],
) -> None:
    plan_repo, _, _ = import_repos
    plan_repo.create(PlanCreateDto(name="Household Budget", initial_balance=0.0))
    plan_repo.create(PlanCreateDto(name="Household Budget (imported)", initial_balance=0.0))

    bundle = _bundle_from_payload(_sample_bundle_payload())
    plan_id = import_service.import_bundle(bundle, {})

    created = plan_repo.find_by_id(plan_id)
    assert created is not None
    assert created.name == "Household Budget (imported) (imported)"


@pytest.mark.unit
def test_import_bundle_requires_rate_resolutions_for_conflicts(
    import_service: PlanImportService,
    import_repos: tuple[SqlitePlanRepository, SqliteEntryRepository, SqliteExchangeRateRepository],
) -> None:
    _, _, rate_repo = import_repos
    rate_repo.upsert(
        ExchangeRateUpsertDto(
            from_currency="EUR",
            to_currency="USD",
            rate=1.08,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )
    bundle = _bundle_from_payload(_sample_bundle_payload())

    with pytest.raises(PlanImportError, match="Missing rate resolution for EUR"):
        import_service.import_bundle(bundle, {})


@pytest.mark.unit
def test_import_bundle_use_file_overwrites_conflict_only(
    import_service: PlanImportService,
    import_repos: tuple[SqlitePlanRepository, SqliteEntryRepository, SqliteExchangeRateRepository],
) -> None:
    _, _, rate_repo = import_repos
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
    bundle = _bundle_from_payload(_sample_bundle_payload())

    import_service.import_bundle(bundle, {"EUR": "use_file"})

    rates = {(rate.from_currency, rate.to_currency): rate.rate for rate in rate_repo.get_all()}
    assert rates[("EUR", "USD")] == 1.15
    assert rates[("GBP", "USD")] == 1.25
    assert rates[("JPY", "USD")] == 0.0067


@pytest.mark.unit
def test_import_bundle_keep_leaves_existing_rate_unchanged(
    import_service: PlanImportService,
    import_repos: tuple[SqlitePlanRepository, SqliteEntryRepository, SqliteExchangeRateRepository],
) -> None:
    _, _, rate_repo = import_repos
    rate_repo.upsert(
        ExchangeRateUpsertDto(
            from_currency="EUR",
            to_currency="USD",
            rate=1.08,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )
    bundle = _bundle_from_payload(_sample_bundle_payload())

    import_service.import_bundle(bundle, {"EUR": "keep"})

    rates = {(rate.from_currency, rate.to_currency): rate.rate for rate in rate_repo.get_all()}
    assert rates[("EUR", "USD")] == 1.08


@pytest.mark.unit
def test_import_bundle_invalid_date_pattern_raises_without_partial_writes(
    import_service: PlanImportService,
    import_repos: tuple[SqlitePlanRepository, SqliteEntryRepository, SqliteExchangeRateRepository],
) -> None:
    plan_repo, entry_repo, _ = import_repos
    bundle = _bundle_from_payload(_sample_bundle_payload(date_pattern="not-a-pattern"))

    with pytest.raises(PlanImportError, match="Invalid date pattern"):
        import_service.import_bundle(bundle, {})

    assert plan_repo.find_all() == []
    assert entry_repo.find_by_plan_id("any") == []
