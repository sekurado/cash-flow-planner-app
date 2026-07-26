from __future__ import annotations

from datetime import date

import pytest
from PySide6.QtCore import QThreadPool

from src.app.workers.simulation_worker import SimulationWorker
from src.data.repositories.entry_repo import EntryCreateDto, SqliteEntryRepository
from src.data.repositories.exchange_rate_repo import SqliteExchangeRateRepository
from src.data.repositories.plan_repo import PlanCreateDto, SqlitePlanRepository
from src.domain.entities import EntryType, SimulationParams
from src.domain.exceptions import SimulationOverflowError


@pytest.fixture
def sample_plan(plan_repository: SqlitePlanRepository) -> str:
    plan = plan_repository.create(
        PlanCreateDto(name="Test Plan", base_currency="USD", initial_balance=1000.0)
    )
    return plan.id


@pytest.mark.integration
def test_worker_emits_finished_with_result_dict(
    qtbot: object,
    sample_plan: str,
    entry_repository: SqliteEntryRepository,
    exchange_rate_repository: SqliteExchangeRateRepository,
) -> None:
    entry_repository.create(
        EntryCreateDto(
            plan_id=sample_plan,
            entry_type=EntryType.INCOME,
            name="Salary",
            date_pattern="1..",
            amount=500.0,
            currency="USD",
        )
    )
    params = SimulationParams(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        initial_balance=1000.0,
        base_currency="USD",
    )
    worker = SimulationWorker(
        entry_repository,
        exchange_rate_repository,
        sample_plan,
        params,
    )

    with qtbot.waitSignal(worker.signals.finished, timeout=5000) as blocker:  # type: ignore[attr-defined]
        QThreadPool.globalInstance().start(worker)

    result = blocker.args[0]
    assert isinstance(result, dict)
    assert result["plan_id"] == sample_plan
    assert result["final_balance"] > 1000.0
    assert result["daily_balances"]
    assert result["monthly_snapshots"]
    assert result["params"]["start_date"] == "2026-01-01"


@pytest.mark.integration
def test_worker_emits_error_on_simulation_overflow(
    qtbot: object,
    sample_plan: str,
    entry_repository: SqliteEntryRepository,
    exchange_rate_repository: SqliteExchangeRateRepository,
) -> None:
    params = SimulationParams(
        start_date=date(2020, 1, 1),
        end_date=date(2030, 1, 2),
        initial_balance=0.0,
        base_currency="USD",
    )
    worker = SimulationWorker(
        entry_repository,
        exchange_rate_repository,
        sample_plan,
        params,
    )

    with qtbot.waitSignal(worker.signals.error, timeout=5000) as blocker:  # type: ignore[attr-defined]
        QThreadPool.globalInstance().start(worker)

    message = blocker.args[0]
    assert SimulationOverflowError.__name__ in message or "10-year" in message


@pytest.mark.integration
def test_worker_never_raises_unhandled_exception(
    qtbot: object,
    sample_plan: str,
    entry_repository: SqliteEntryRepository,
    exchange_rate_repository: SqliteExchangeRateRepository,
) -> None:
    entry_repository.create(
        EntryCreateDto(
            plan_id=sample_plan,
            entry_type=EntryType.EXPENSE,
            name="Bad pattern",
            date_pattern="not-a-pattern",
            amount=100.0,
            currency="USD",
        )
    )
    params = SimulationParams(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        initial_balance=1000.0,
        base_currency="USD",
    )
    worker = SimulationWorker(
        entry_repository,
        exchange_rate_repository,
        sample_plan,
        params,
    )

    with qtbot.waitSignal(worker.signals.error, timeout=5000) as blocker:  # type: ignore[attr-defined]
        QThreadPool.globalInstance().start(worker)

    assert blocker.args[0]


@pytest.mark.integration
def test_worker_applies_what_if_overrides_in_memory(
    qtbot: object,
    sample_plan: str,
    entry_repository: SqliteEntryRepository,
    exchange_rate_repository: SqliteExchangeRateRepository,
) -> None:
    entry = entry_repository.create(
        EntryCreateDto(
            plan_id=sample_plan,
            entry_type=EntryType.INCOME,
            name="Salary",
            date_pattern="1..",
            amount=500.0,
            currency="USD",
        )
    )
    params = SimulationParams(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        initial_balance=1000.0,
        base_currency="USD",
    )
    baseline_worker = SimulationWorker(
        entry_repository,
        exchange_rate_repository,
        sample_plan,
        params,
    )
    with qtbot.waitSignal(baseline_worker.signals.finished, timeout=5000) as baseline_blocker:  # type: ignore[attr-defined]
        QThreadPool.globalInstance().start(baseline_worker)
    baseline_balance = baseline_blocker.args[0]["final_balance"]

    what_if_worker = SimulationWorker(
        entry_repository,
        exchange_rate_repository,
        sample_plan,
        params,
        what_if_overrides={entry.id: {"amount": 0}},
    )
    with qtbot.waitSignal(what_if_worker.signals.finished, timeout=5000) as what_if_blocker:  # type: ignore[attr-defined]
        QThreadPool.globalInstance().start(what_if_worker)

    what_if_result = what_if_blocker.args[0]
    assert what_if_result["final_balance"] < baseline_balance
    assert what_if_result["final_balance"] == params.initial_balance

    saved_entry = entry_repository.find_by_id(entry.id)
    assert saved_entry is not None
    assert saved_entry.amount == 500.0
