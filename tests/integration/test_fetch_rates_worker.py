from __future__ import annotations

import pytest
from PySide6.QtCore import QCoreApplication, QSettings, QThreadPool

from src.app.identity import ORGANIZATION_NAME
from src.data.repositories.exchange_rate_repo import SqliteExchangeRateRepository
from src.integrations.exchange_rate_fetcher import (
    _DAILY_FETCH_COUNT_KEY,
    _DAILY_FETCH_DATE_KEY,
    _LAST_FETCH_AT_KEY,
    FetchRatesWorker,
    configure_dev_mode,
    set_use_mock_rates,
)

_MOCK_RATES = {"EUR": 0.85, "GBP": 0.75}


@pytest.fixture(autouse=True)
def clear_last_fetch_date(qt_app: object) -> None:
    _ = qt_app
    QCoreApplication.setOrganizationName(ORGANIZATION_NAME)
    QCoreApplication.setApplicationName("CashFlowPlannerDesktopFetcherWorkerTest")
    settings = QSettings()
    settings.remove(_LAST_FETCH_AT_KEY)
    settings.remove(_DAILY_FETCH_DATE_KEY)
    settings.remove(_DAILY_FETCH_COUNT_KEY)
    settings.sync()
    configure_dev_mode(enabled=False)


@pytest.fixture(autouse=True)
def reset_dev_mode() -> None:
    configure_dev_mode(enabled=False)
    yield
    configure_dev_mode(enabled=False)


@pytest.mark.integration
def test_worker_emits_finished_with_rate_dict(
    qtbot: object,
    monkeypatch: pytest.MonkeyPatch,
    exchange_rate_repository: SqliteExchangeRateRepository,
) -> None:
    monkeypatch.setattr(
        "src.integrations.exchange_rate_fetcher.fetch_rates",
        lambda base, symbols: _MOCK_RATES,
    )

    worker = FetchRatesWorker(
        exchange_rate_repository,
        "USD",
        ["EUR", "GBP"],
    )

    with qtbot.waitSignal(worker.signals.finished, timeout=5000) as blocker:  # type: ignore[attr-defined]
        QThreadPool.globalInstance().start(worker)

    rates = blocker.args[0]
    assert rates == _MOCK_RATES

    stored = exchange_rate_repository.get_all()
    assert len(stored) == 2
    by_from = {rate.from_currency: rate for rate in stored}
    assert by_from["EUR"].to_currency == "USD"
    assert by_from["GBP"].to_currency == "USD"
    assert by_from["EUR"].rate == pytest.approx(1 / 0.85)
    assert by_from["GBP"].rate == pytest.approx(1 / 0.75)
    assert QSettings().value(_LAST_FETCH_AT_KEY) is not None
    assert QSettings().value(_DAILY_FETCH_COUNT_KEY) == 1


@pytest.mark.integration
def test_worker_emits_error_on_fetch_failure(
    qtbot: object,
    monkeypatch: pytest.MonkeyPatch,
    exchange_rate_repository: SqliteExchangeRateRepository,
) -> None:
    def _raise_fetch_error(base: str, symbols: list[str]) -> dict[str, float]:
        msg = "Network unavailable"
        raise RuntimeError(msg)

    monkeypatch.setattr(
        "src.integrations.exchange_rate_fetcher.fetch_rates",
        _raise_fetch_error,
    )

    worker = FetchRatesWorker(
        exchange_rate_repository,
        "USD",
        ["EUR"],
    )

    with qtbot.waitSignal(worker.signals.error, timeout=5000) as blocker:  # type: ignore[attr-defined]
        QThreadPool.globalInstance().start(worker)

    assert blocker.args[0] == "Network unavailable"
    assert exchange_rate_repository.get_all() == []


@pytest.mark.integration
def test_worker_uses_mock_rates_without_http(
    qtbot: object,
    exchange_rate_repository: SqliteExchangeRateRepository,
) -> None:
    configure_dev_mode(enabled=True)
    set_use_mock_rates(True)

    worker = FetchRatesWorker(
        exchange_rate_repository,
        "USD",
        ["EUR", "GBP"],
    )

    with qtbot.waitSignal(worker.signals.finished, timeout=5000) as blocker:  # type: ignore[attr-defined]
        QThreadPool.globalInstance().start(worker)

    rates = blocker.args[0]
    assert rates == {"EUR": 0.92, "GBP": 0.79}

    stored = exchange_rate_repository.get_all()
    assert len(stored) == 2
    by_from = {rate.from_currency: rate for rate in stored}
    assert by_from["EUR"].rate == pytest.approx(1 / 0.92)
    assert by_from["GBP"].rate == pytest.approx(1 / 0.79)
    assert QSettings().value(_LAST_FETCH_AT_KEY) is None


@pytest.mark.integration
def test_worker_upserts_on_repeated_mock_fetches_same_day(
    qtbot: object,
    exchange_rate_repository: SqliteExchangeRateRepository,
) -> None:
    configure_dev_mode(enabled=True)
    set_use_mock_rates(True)

    for _ in range(2):
        worker = FetchRatesWorker(
            exchange_rate_repository,
            "USD",
            ["EUR", "GBP"],
        )
        with qtbot.waitSignal(worker.signals.finished, timeout=5000):  # type: ignore[attr-defined]
            QThreadPool.globalInstance().start(worker)
            QThreadPool.globalInstance().waitForDone(5000)

    assert len(exchange_rate_repository.get_all()) == 2
    assert QSettings().value(_LAST_FETCH_AT_KEY) is None
