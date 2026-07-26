from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import date

import pytest
from PySide6.QtCore import QThreadPool

from src.app.viewmodels.simulation_vm import SimulationViewModel
from src.app.viewmodels.suggestions_vm import SuggestionsViewModel
from src.data.repositories.entry_repo import EntryCreateDto, SqliteEntryRepository
from src.data.repositories.exchange_rate_repo import SqliteExchangeRateRepository
from src.data.repositories.plan_repo import PlanCreateDto, SqlitePlanRepository
from src.domain.entities import Entry, EntryType, SimulationResult
from src.domain.exceptions import SuggestionAnalysisError
from src.domain.suggestions import Suggestion, SuggestionEngine


def _simulation_params(
    *,
    start: date = date(2026, 1, 1),
    end: date = date(2026, 3, 31),
    initial_balance: float = 200.0,
    base_currency: str = "USD",
) -> dict[str, object]:
    return {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "initial_balance": initial_balance,
        "base_currency": base_currency,
    }


@pytest.fixture
def deficit_plan(plan_repository: SqlitePlanRepository) -> str:
    plan = plan_repository.create(
        PlanCreateDto(name="Deficit Plan", base_currency="USD", initial_balance=200.0)
    )
    return plan.id


@pytest.fixture
def suggestions_vm(
    qt_app: object,
    entry_repository: SqliteEntryRepository,
) -> SuggestionsViewModel:
    _ = qt_app
    return SuggestionsViewModel(entry_repository)


@pytest.fixture
def wired_simulation_vm(
    qt_app: object,
    entry_repository: SqliteEntryRepository,
    exchange_rate_repository: SqliteExchangeRateRepository,
    suggestions_vm: SuggestionsViewModel,
) -> SimulationViewModel:
    _ = qt_app
    return SimulationViewModel(
        entry_repository,
        exchange_rate_repository,
        suggestions_vm,
    )


def _wait_for_thread_pool() -> None:
    QThreadPool.globalInstance().waitForDone(5000)


def _seed_deficit_entries(entry_repository: SqliteEntryRepository, plan_id: str) -> None:
    entry_repository.create(
        EntryCreateDto(
            plan_id=plan_id,
            entry_type=EntryType.INCOME,
            name="Salary",
            date_pattern="1..",
            amount=500.0,
            currency="USD",
        )
    )
    entry_repository.create(
        EntryCreateDto(
            plan_id=plan_id,
            entry_type=EntryType.EXPENSE,
            name="Rent",
            date_pattern="5..",
            amount=900.0,
            currency="USD",
        )
    )
    entry_repository.create(
        EntryCreateDto(
            plan_id=plan_id,
            entry_type=EntryType.EXPENSE,
            name="Equipment",
            date_pattern="3.1.2026",
            amount=400.0,
            currency="USD",
        )
    )


@pytest.mark.integration
def test_baseline_simulation_refreshes_suggestions_for_deficit_plan(
    qtbot: object,
    wired_simulation_vm: SimulationViewModel,
    suggestions_vm: SuggestionsViewModel,
    deficit_plan: str,
    entry_repository: SqliteEntryRepository,
) -> None:
    _seed_deficit_entries(entry_repository, deficit_plan)

    wired_simulation_vm.runSimulation(deficit_plan, _simulation_params())

    with qtbot.waitSignal(wired_simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass
    _wait_for_thread_pool()
    with qtbot.waitSignal(suggestions_vm.hasSuggestionsChanged, timeout=5000):  # type: ignore[attr-defined]
        pass

    assert suggestions_vm.error == ""
    assert suggestions_vm.isAnalyzing is False
    assert suggestions_vm.hasSuggestions is True
    assert suggestions_vm.suggestions.item_count() > 0

    first = suggestions_vm.suggestionAt(0)
    assert first is not None
    assert first["title"]
    assert first["kind"]
    assert first["impactFormatted"] or first["impactAmount"] is None


@pytest.mark.integration
def test_what_if_simulation_does_not_refresh_suggestions(
    qtbot: object,
    wired_simulation_vm: SimulationViewModel,
    suggestions_vm: SuggestionsViewModel,
    deficit_plan: str,
    entry_repository: SqliteEntryRepository,
) -> None:
    _seed_deficit_entries(entry_repository, deficit_plan)
    rent_entry = next(
        entry for entry in entry_repository.find_by_plan_id(deficit_plan) if entry.name == "Rent"
    )

    wired_simulation_vm.runSimulation(deficit_plan, _simulation_params())
    with qtbot.waitSignal(wired_simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass
    _wait_for_thread_pool()
    with qtbot.waitSignal(suggestions_vm.hasSuggestionsChanged, timeout=5000):  # type: ignore[attr-defined]
        pass
    baseline_count = suggestions_vm.suggestions.item_count()
    assert baseline_count > 0

    wired_simulation_vm.runWhatIf(
        deficit_plan,
        _simulation_params(),
        {rent_entry.id: {"amount": 100.0}},
    )
    with qtbot.waitSignal(wired_simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass
    _wait_for_thread_pool()

    assert suggestions_vm.suggestions.item_count() == baseline_count


def _minimal_result(plan_id: str) -> dict[str, object]:
    return {
        "plan_id": plan_id,
        "params": {
            "start_date": "2026-01-01",
            "end_date": "2026-03-31",
            "initial_balance": 200.0,
            "base_currency": "USD",
        },
        "daily_balances": [],
        "monthly_snapshots": [],
        "first_deficit_date": "2026-02-05",
        "final_balance": -100.0,
        "total_income": 1500.0,
        "total_expense": 1800.0,
    }


@pytest.mark.integration
def test_analysis_error_sets_error_without_propagating(
    qtbot: object,
    entry_repository: SqliteEntryRepository,
    deficit_plan: str,
) -> None:
    def failing_analyzer(
        entries: Sequence[Entry],
        result: SimulationResult,
    ) -> Iterable[Suggestion]:
        del entries, result
        raise SuggestionAnalysisError("analysis failed")

    vm = SuggestionsViewModel(
        entry_repository,
        engine=SuggestionEngine(analyzers=[failing_analyzer]),
    )

    vm.refreshForPlan(deficit_plan, _minimal_result(deficit_plan))
    with qtbot.waitSignal(vm.errorChanged, timeout=5000):  # type: ignore[attr-defined]
        pass
    _wait_for_thread_pool()

    assert vm.error != ""
    assert "analysis failed" in vm.error
    assert vm.hasSuggestions is False
    assert vm.isAnalyzing is False


@pytest.mark.integration
def test_clear_result_clears_suggestions(
    qtbot: object,
    wired_simulation_vm: SimulationViewModel,
    suggestions_vm: SuggestionsViewModel,
    deficit_plan: str,
    entry_repository: SqliteEntryRepository,
) -> None:
    _seed_deficit_entries(entry_repository, deficit_plan)

    wired_simulation_vm.runSimulation(deficit_plan, _simulation_params())
    with qtbot.waitSignal(wired_simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass
    _wait_for_thread_pool()
    with qtbot.waitSignal(suggestions_vm.hasSuggestionsChanged, timeout=5000):  # type: ignore[attr-defined]
        pass
    assert suggestions_vm.hasSuggestions is True

    wired_simulation_vm.clearResult()
    assert suggestions_vm.hasSuggestions is False
    assert suggestions_vm.suggestions.item_count() == 0
