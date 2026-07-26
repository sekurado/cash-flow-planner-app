from __future__ import annotations

from datetime import date

import pytest
from PySide6.QtCore import QCoreApplication, QSettings, QThreadPool

from src.app.identity import ORGANIZATION_NAME
from src.app.viewmodels.simulation_vm import SimulationViewModel
from src.data.repositories.entry_repo import EntryCreateDto, SqliteEntryRepository
from src.data.repositories.exchange_rate_repo import (
    ExchangeRateUpsertDto,
    SqliteExchangeRateRepository,
)
from src.data.repositories.plan_repo import PlanCreateDto, SqlitePlanRepository
from src.domain.entities import EntryType
from src.domain.exceptions import SimulationOverflowError
from src.integrations.exchange_rate_fetcher import (
    _DAILY_FETCH_COUNT_KEY,
    _DAILY_FETCH_DATE_KEY,
    _LAST_FETCH_AT_KEY,
    _MAX_DAILY_FETCHES,
    configure_dev_mode,
    record_successful_fetch,
    set_use_mock_rates,
)

_LIVE_RATES_ENABLED_KEY = "exchange_rate_api_enabled"


@pytest.fixture
def sample_plan(plan_repository: SqlitePlanRepository) -> str:
    plan = plan_repository.create(
        PlanCreateDto(name="Test Plan", base_currency="USD", initial_balance=1000.0)
    )
    return plan.id


def _simulation_params(
    *,
    start: date = date(2026, 1, 1),
    end: date = date(2026, 12, 31),
    initial_balance: float = 1000.0,
    base_currency: str = "USD",
) -> dict[str, object]:
    return {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "initial_balance": initial_balance,
        "base_currency": base_currency,
    }


@pytest.fixture
def simulation_vm(
    qt_app: object,
    entry_repository: SqliteEntryRepository,
    exchange_rate_repository: SqliteExchangeRateRepository,
) -> SimulationViewModel:
    _ = qt_app
    QCoreApplication.setOrganizationName(ORGANIZATION_NAME)
    QCoreApplication.setApplicationName("CashFlowPlannerDesktopSimulationVmTest")
    settings = QSettings()
    settings.remove(_LIVE_RATES_ENABLED_KEY)
    settings.remove(_LAST_FETCH_AT_KEY)
    settings.remove(_DAILY_FETCH_DATE_KEY)
    settings.remove(_DAILY_FETCH_COUNT_KEY)
    settings.sync()
    configure_dev_mode(enabled=False)
    return SimulationViewModel(entry_repository, exchange_rate_repository)


@pytest.fixture(autouse=True)
def reset_dev_mode() -> None:
    configure_dev_mode(enabled=False)
    yield
    configure_dev_mode(enabled=False)


@pytest.mark.integration
def test_run_simulation_transitions_is_running_and_sets_result(
    qtbot: object,
    simulation_vm: SimulationViewModel,
    sample_plan: str,
    entry_repository: SqliteEntryRepository,
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
    assert simulation_vm.isRunning is False

    simulation_vm.runSimulation(sample_plan, _simulation_params())
    assert simulation_vm.isRunning is True

    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass

    assert simulation_vm.isRunning is False
    assert simulation_vm.result is not None
    assert simulation_vm.error == ""


@pytest.mark.integration
def test_run_simulation_overflow_sets_error_and_stops_running(
    qtbot: object,
    simulation_vm: SimulationViewModel,
    sample_plan: str,
) -> None:
    assert simulation_vm.isRunning is False

    simulation_vm.runSimulation(
        sample_plan,
        _simulation_params(
            start=date(2020, 1, 1),
            end=date(2030, 1, 2),
            initial_balance=0.0,
        ),
    )
    assert simulation_vm.isRunning is True

    with qtbot.waitSignal(simulation_vm.errorChanged, timeout=5000) as blocker:  # type: ignore[attr-defined]
        pass

    message = blocker.args[0] if blocker.args else simulation_vm.error
    assert message != ""
    assert SimulationOverflowError.__name__ in message or "10-year" in message
    assert simulation_vm.isRunning is False
    assert simulation_vm.result is None


@pytest.mark.integration
def test_run_what_if_deactivated_entry_excluded_from_result(
    qtbot: object,
    simulation_vm: SimulationViewModel,
    sample_plan: str,
    entry_repository: SqliteEntryRepository,
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
    params = _simulation_params()

    simulation_vm.runSimulation(sample_plan, params)
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass
    baseline_balance = simulation_vm.result["final_balance"]  # type: ignore[index]

    simulation_vm.runWhatIf(
        sample_plan,
        params,
        {entry.id: {"is_active": False}},
    )
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass

    assert simulation_vm.isRunning is False
    assert simulation_vm.error == ""
    what_if_balance = simulation_vm.result["final_balance"]  # type: ignore[index]
    assert what_if_balance < baseline_balance
    assert what_if_balance == params["initial_balance"]
    assert simulation_vm.isScenarioResult is True


@pytest.mark.integration
def test_baseline_simulation_clears_scenario_result_flag(
    qtbot: object,
    simulation_vm: SimulationViewModel,
    sample_plan: str,
    entry_repository: SqliteEntryRepository,
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
    params = _simulation_params()

    simulation_vm.runWhatIf(
        sample_plan,
        params,
        {entry.id: {"is_active": False}},
    )
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass
    assert simulation_vm.isScenarioResult is True

    simulation_vm.runSimulation(sample_plan, params)
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass

    assert simulation_vm.isScenarioResult is False


@pytest.mark.integration
def test_run_what_if_zero_amount_excludes_entry_contribution(
    qtbot: object,
    simulation_vm: SimulationViewModel,
    sample_plan: str,
    entry_repository: SqliteEntryRepository,
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
    params = _simulation_params()

    simulation_vm.runSimulation(sample_plan, params)
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass
    baseline_balance = simulation_vm.result["final_balance"]  # type: ignore[index]

    simulation_vm.runWhatIf(
        sample_plan,
        params,
        {entry.id: {"amount": 0}},
    )
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass

    assert simulation_vm.error == ""
    what_if_balance = simulation_vm.result["final_balance"]  # type: ignore[index]
    assert what_if_balance < baseline_balance
    assert what_if_balance == params["initial_balance"]


@pytest.mark.integration
def test_run_what_if_does_not_persist_overrides(
    qtbot: object,
    simulation_vm: SimulationViewModel,
    sample_plan: str,
    entry_repository: SqliteEntryRepository,
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
    params = _simulation_params()

    simulation_vm.runSimulation(sample_plan, params)
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass
    baseline_balance = simulation_vm.result["final_balance"]  # type: ignore[index]

    simulation_vm.runWhatIf(
        sample_plan,
        params,
        {entry.id: {"amount": 0}},
    )
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass

    simulation_vm.runSimulation(sample_plan, params)
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass

    assert simulation_vm.error == ""
    assert simulation_vm.result["final_balance"] == baseline_balance  # type: ignore[index]
    saved_entry = entry_repository.find_by_id(entry.id)
    assert saved_entry is not None
    assert saved_entry.amount == 500.0
    assert saved_entry.is_active is True


@pytest.mark.integration
def test_snapshot_model_populated_after_simulation(
    qtbot: object,
    simulation_vm: SimulationViewModel,
    sample_plan: str,
    entry_repository: SqliteEntryRepository,
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
    assert simulation_vm.snapshotModel.rowCount() == 0

    simulation_vm.runSimulation(sample_plan, _simulation_params())
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass

    snapshot_model = simulation_vm.snapshotModel
    assert snapshot_model.rowCount() == 12
    first_index = snapshot_model.index(0, 0)
    assert snapshot_model.data(first_index, snapshot_model.TOTAL_INCOME_ROLE) == 500.0
    assert snapshot_model.data(first_index, snapshot_model.DEFICIT_ROLE) is False


@pytest.mark.integration
def test_clear_result_clears_snapshot_model(
    qtbot: object,
    simulation_vm: SimulationViewModel,
    sample_plan: str,
    entry_repository: SqliteEntryRepository,
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

    simulation_vm.runSimulation(sample_plan, _simulation_params())
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass
    assert simulation_vm.snapshotModel.rowCount() > 0

    simulation_vm.clearResult()

    assert simulation_vm.result is None
    assert simulation_vm.snapshotModel.rowCount() == 0


@pytest.mark.integration
def test_clear_result_sets_result_to_none(
    qtbot: object,
    simulation_vm: SimulationViewModel,
    sample_plan: str,
    entry_repository: SqliteEntryRepository,
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

    simulation_vm.runSimulation(sample_plan, _simulation_params())
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass
    assert simulation_vm.result is not None

    simulation_vm.clearResult()

    assert simulation_vm.result is None


@pytest.mark.integration
def test_fetch_live_rates_disabled_sets_error(
    simulation_vm: SimulationViewModel,
    sample_plan: str,
) -> None:
    simulation_vm.fetchLiveRates("USD")

    assert simulation_vm.error != ""
    assert simulation_vm.isFetchingRates is False


@pytest.mark.integration
def test_fetch_live_rates_blocked_during_minute_cooldown(
    simulation_vm: SimulationViewModel,
    sample_plan: str,
) -> None:
    QSettings().setValue(_LIVE_RATES_ENABLED_KEY, True)
    record_successful_fetch()

    simulation_vm.fetchLiveRates("USD")

    assert "before fetching live rates again" in simulation_vm.error
    assert simulation_vm.isFetchingRates is False


@pytest.mark.integration
def test_fetch_live_rates_blocked_when_daily_limit_reached(
    simulation_vm: SimulationViewModel,
    sample_plan: str,
) -> None:
    QSettings().setValue(_LIVE_RATES_ENABLED_KEY, True)
    QSettings().setValue(_DAILY_FETCH_DATE_KEY, date.today().isoformat())
    QSettings().setValue(_DAILY_FETCH_COUNT_KEY, _MAX_DAILY_FETCHES)

    simulation_vm.fetchLiveRates("EUR")

    assert "Daily live rate fetch limit reached" in simulation_vm.error
    assert simulation_vm.isFetchingRates is False


@pytest.mark.integration
def test_fetch_live_rates_starts_worker_when_enabled(
    qtbot: object,
    monkeypatch: pytest.MonkeyPatch,
    simulation_vm: SimulationViewModel,
    sample_plan: str,
    exchange_rate_repository: SqliteExchangeRateRepository,
) -> None:
    QSettings().setValue(_LIVE_RATES_ENABLED_KEY, True)
    monkeypatch.setattr(
        "src.integrations.exchange_rate_fetcher.fetch_rates",
        lambda base, symbols: {"EUR": 0.85, "GBP": 0.75},
    )

    simulation_vm.fetchLiveRates("USD")
    assert simulation_vm.isFetchingRates is True

    with qtbot.waitSignal(simulation_vm.liveRatesFetched, timeout=5000):  # type: ignore[attr-defined]
        QThreadPool.globalInstance().waitForDone(5000)

    assert simulation_vm.isFetchingRates is False
    assert simulation_vm.error == ""
    assert len(exchange_rate_repository.get_all()) == 2


@pytest.mark.integration
def test_fetch_live_rates_uses_mock(
    qtbot: object,
    simulation_vm: SimulationViewModel,
    sample_plan: str,
    exchange_rate_repository: SqliteExchangeRateRepository,
) -> None:
    configure_dev_mode(enabled=True)
    set_use_mock_rates(True)
    QSettings().setValue(_LIVE_RATES_ENABLED_KEY, True)

    simulation_vm.fetchLiveRates("USD")

    with qtbot.waitSignal(simulation_vm.liveRatesFetched, timeout=5000):  # type: ignore[attr-defined]
        QThreadPool.globalInstance().waitForDone(5000)

    assert simulation_vm.error == ""
    assert len(exchange_rate_repository.get_all()) == 62


@pytest.mark.integration
def test_fetch_live_rates_allows_repeated_mock_fetches_same_day(
    qtbot: object,
    simulation_vm: SimulationViewModel,
    sample_plan: str,
) -> None:
    configure_dev_mode(enabled=True)
    set_use_mock_rates(True)
    QSettings().setValue(_LIVE_RATES_ENABLED_KEY, True)
    record_successful_fetch()

    simulation_vm.fetchLiveRates("USD")

    with qtbot.waitSignal(simulation_vm.liveRatesFetched, timeout=5000):  # type: ignore[attr-defined]
        QThreadPool.globalInstance().waitForDone(5000)

    assert simulation_vm.error == ""
    assert simulation_vm.isFetchingRates is False


@pytest.mark.integration
def test_display_currency_converts_usd_amounts(
    qt_app: object,
    simulation_vm: SimulationViewModel,
    exchange_rate_repository: SqliteExchangeRateRepository,
) -> None:
    _ = qt_app
    exchange_rate_repository.upsert(
        ExchangeRateUpsertDto(
            from_currency="EUR",
            to_currency="USD",
            rate=1.1,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )
    simulation_vm.refreshDisplayCurrencies()

    assert simulation_vm.displayCurrencies == ["USD", "EUR"]
    simulation_vm.setDisplayCurrency("EUR")

    assert simulation_vm.convertToDisplayAmount(110.0) == pytest.approx(100.0)
    assert simulation_vm.displayCurrency == "EUR"


@pytest.mark.integration
def test_set_active_plan_restores_saved_display_currency(
    qt_app: object,
    simulation_vm: SimulationViewModel,
    sample_plan: str,
    exchange_rate_repository: SqliteExchangeRateRepository,
) -> None:
    _ = qt_app
    exchange_rate_repository.upsert(
        ExchangeRateUpsertDto(
            from_currency="EUR",
            to_currency="USD",
            rate=1.1,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )
    simulation_vm.refreshDisplayCurrencies()
    simulation_vm.setActivePlan(sample_plan, "USD")
    simulation_vm.setDisplayCurrency("EUR")

    simulation_vm.setActivePlan("", "USD")
    simulation_vm.setActivePlan(sample_plan, "USD")

    assert simulation_vm.displayCurrency == "EUR"


@pytest.mark.integration
def test_eur_base_plan_defaults_display_currency_to_eur(
    qt_app: object,
    simulation_vm: SimulationViewModel,
    plan_repository: SqlitePlanRepository,
    exchange_rate_repository: SqliteExchangeRateRepository,
) -> None:
    _ = qt_app
    plan = plan_repository.create(
        PlanCreateDto(name="EUR Plan", base_currency="EUR", initial_balance=1000.0)
    )
    exchange_rate_repository.upsert(
        ExchangeRateUpsertDto(
            from_currency="USD",
            to_currency="EUR",
            rate=0.9,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )

    simulation_vm.setActivePlan(plan.id, "EUR")

    assert simulation_vm.displayCurrency == "EUR"
    assert simulation_vm.displayCurrencies == ["EUR", "USD"]


@pytest.mark.integration
def test_eur_base_plan_converts_amounts_from_eur_to_display_currency(
    qt_app: object,
    simulation_vm: SimulationViewModel,
    plan_repository: SqlitePlanRepository,
    exchange_rate_repository: SqliteExchangeRateRepository,
) -> None:
    _ = qt_app
    plan = plan_repository.create(
        PlanCreateDto(name="EUR Plan", base_currency="EUR", initial_balance=1000.0)
    )
    exchange_rate_repository.upsert(
        ExchangeRateUpsertDto(
            from_currency="USD",
            to_currency="EUR",
            rate=0.9,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )
    simulation_vm.setActivePlan(plan.id, "EUR")
    simulation_vm.setDisplayCurrency("USD")

    assert simulation_vm.convertToDisplayAmount(90.0) == pytest.approx(100.0)


@pytest.mark.integration
def test_prefill_what_if_override_emits_signal(
    qtbot: object,
    simulation_vm: SimulationViewModel,
) -> None:
    change_json = '{"amount_delta": -100.0}'

    with qtbot.waitSignal(simulation_vm.whatIfPrefillRequested, timeout=1000) as blocker:  # type: ignore[attr-defined]
        simulation_vm.prefillWhatIfOverride("entry-1", change_json)

    assert blocker.args == ["entry-1", change_json]


@pytest.mark.integration
def test_prefill_what_if_override_ignores_empty_payload(
    simulation_vm: SimulationViewModel,
) -> None:
    simulation_vm.prefillWhatIfOverride("", '{"amount_delta": -1}')
    simulation_vm.prefillWhatIfOverride("entry-1", "")
