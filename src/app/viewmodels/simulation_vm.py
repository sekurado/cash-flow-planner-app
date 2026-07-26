from __future__ import annotations

import math
from datetime import date
from typing import Any, cast

from PySide6.QtCore import Property, QObject, QSettings, QThreadPool, Signal, Slot

from src.app.models.snapshot_list_model import SnapshotListModel
from src.app.qml_variant import coerce_mapping
from src.app.version import app_version
from src.app.viewmodels.error_support import ErrorSupport
from src.app.viewmodels.suggestions_vm import SuggestionsViewModel
from src.app.workers.export_worker import ExportFormat, ExportWorker
from src.app.workers.simulation_worker import SimulationWorker
from src.data.repositories.entry_repo import AbstractEntryRepository
from src.data.repositories.exchange_rate_repo import AbstractExchangeRateRepository
from src.domain.currencies import COMMON_CURRENCIES
from src.domain.currency_normalizer import convert_amount, display_currencies
from src.domain.entities import ExchangeRate, MonthlySnapshot, SimulationParams
from src.integrations.exchange_rate_fetcher import (
    FetchRatesWorker,
    can_fetch_live_rates,
    is_daily_fetch_limit_reached,
    seconds_until_next_fetch,
)

_LIVE_RATES_ENABLED_KEY = "exchange_rate_api_enabled"
_LIVE_RATES_DISABLED_MSG = "Live exchange-rate fetching is not enabled."
_LIVE_RATES_DAILY_LIMIT_MSG = (
    "Daily live rate fetch limit reached (10 per day). Try again tomorrow."
)
_LIVE_RATES_COOLDOWN_SECONDS_MSG = (
    "Please wait {seconds} second(s) before fetching live rates again."
)
_LIVE_RATES_COOLDOWN_MINUTES_MSG = (
    "Please wait {minutes} minute(s) before fetching live rates again."
)
_NO_RESULT_MSG = "No simulation result to export."
_USD = "USD"
_DISPLAY_CURRENCY_KEY_PREFIX = "simulation/display_currency/"


def _display_currency_settings_key(plan_id: str) -> str:
    return f"{_DISPLAY_CURRENCY_KEY_PREFIX}{plan_id}"


def _settings_bool(value: object, *, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes"}
    return bool(value)


def _is_live_rates_enabled() -> bool:
    return _settings_bool(QSettings().value(_LIVE_RATES_ENABLED_KEY), default=False)


def _parse_date(value: object) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    msg = f"Expected date or ISO date string, got {type(value).__name__}"
    raise TypeError(msg)


def _parse_params(raw: object) -> SimulationParams:
    data = coerce_mapping(raw, label="Simulation params")
    initial_balance = data.get("initial_balance")
    base_currency = data.get("base_currency")
    if not isinstance(initial_balance, (int, float)):
        msg = "Simulation params must include a numeric initial_balance"
        raise TypeError(msg)
    if not isinstance(base_currency, str) or not base_currency:
        msg = "Simulation params must include a non-empty base_currency"
        raise TypeError(msg)
    return SimulationParams(
        start_date=_parse_date(data["start_date"]),
        end_date=_parse_date(data["end_date"]),
        initial_balance=float(initial_balance),
        base_currency=base_currency,
    )


def _parse_overrides(raw: object) -> dict[str, dict[str, object]]:
    return cast(dict[str, dict[str, object]], coerce_mapping(raw, label="What-if overrides"))


def _parse_monthly_snapshots(result: dict[str, Any] | None) -> list[MonthlySnapshot]:
    if result is None:
        return []
    raw = result.get("monthly_snapshots")
    if not isinstance(raw, list):
        return []
    snapshots: list[MonthlySnapshot] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        snapshots.append(
            MonthlySnapshot(
                year=int(item["year"]),
                month=int(item["month"]),
                total_income=float(item["total_income"]),
                total_expense=float(item["total_expense"]),
                net_flow=float(item["net_flow"]),
                closing_balance=float(item["closing_balance"]),
                deficit=bool(item["deficit"]),
            )
        )
    return snapshots


class SimulationViewModel(QObject):
    """Exposes simulation runs and results to QML via background workers."""

    isRunningChanged = Signal()
    isFetchingRatesChanged = Signal()
    resultChanged = Signal()
    errorChanged = Signal()
    exportSucceeded = Signal()
    liveRatesFetched = Signal()
    displayCurrencyChanged = Signal()
    displayCurrenciesChanged = Signal()
    activePlanChanged = Signal()
    isScenarioResultChanged = Signal()
    whatIfPrefillRequested = Signal(str, str)

    def __init__(
        self,
        entry_repo: AbstractEntryRepository,
        exchange_rate_repo: AbstractExchangeRateRepository,
        suggestions_vm: SuggestionsViewModel | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._entry_repo = entry_repo
        self._exchange_rate_repo = exchange_rate_repo
        self._suggestions_vm = suggestions_vm
        self._is_running = False
        self._is_fetching_rates = False
        self._result: dict[str, Any] | None = None
        self._errors = ErrorSupport(self)
        self._worker: SimulationWorker | None = None
        self._fetch_rates_worker: FetchRatesWorker | None = None
        self._export_worker: ExportWorker | None = None
        self._what_if_overrides: dict[str, dict[str, object]] | None = None
        self._snapshot_model = SnapshotListModel(parent=self)
        self._active_plan_id = ""
        self._plan_base_currency = _USD
        self._display_currency = _USD
        self._display_currencies: list[str] = [_USD]
        self._exchange_rates_cache: list[ExchangeRate] = []
        self._refresh_display_currencies()

    @Property(str, notify=activePlanChanged)
    def activePlanId(self) -> str:
        return self._active_plan_id

    @Property(str, notify=displayCurrencyChanged)
    def displayCurrency(self) -> str:
        return self._display_currency

    @Property("QVariantList", notify=displayCurrenciesChanged)  # type: ignore[arg-type]
    def displayCurrencies(self) -> list[str]:
        return self._display_currencies

    @Property(bool, notify=isRunningChanged)
    def isRunning(self) -> bool:
        return self._is_running

    @Property(bool, notify=isScenarioResultChanged)
    def isScenarioResult(self) -> bool:
        return self._what_if_overrides is not None

    @Property(bool, notify=isFetchingRatesChanged)
    def isFetchingRates(self) -> bool:
        return self._is_fetching_rates

    @Property("QVariant", notify=resultChanged)  # type: ignore[arg-type]
    def result(self) -> dict[str, Any] | None:
        return self._result

    @Property(QObject, constant=True)
    def snapshotModel(self) -> SnapshotListModel:
        return self._snapshot_model

    @Property(str, notify=errorChanged)
    def error(self) -> str:
        return self._errors.message

    @Slot(str, str)
    def setActivePlan(self, plan_id: str, base_currency: str) -> None:
        if plan_id == self._active_plan_id and base_currency == self._plan_base_currency:
            return
        self._active_plan_id = plan_id
        self._plan_base_currency = base_currency or _USD
        self._refresh_display_currencies()
        saved = QSettings().value(_display_currency_settings_key(plan_id))
        if isinstance(saved, str) and saved in self._display_currencies:
            self._display_currency = saved
        else:
            self._display_currency = self._plan_base_currency
        self.activePlanChanged.emit()
        self.displayCurrencyChanged.emit()

    @Slot(str)
    def setDisplayCurrency(self, currency: str) -> None:
        if currency not in self._display_currencies:
            msg = f"Display currency {currency} is not available"
            self._set_error(msg)
            return
        if currency == self._display_currency:
            return
        self._display_currency = currency
        if self._active_plan_id:
            QSettings().setValue(
                _display_currency_settings_key(self._active_plan_id),
                currency,
            )
        self._clear_error()
        self.displayCurrencyChanged.emit()

    @Slot(float, result=float)
    def convertToDisplayAmount(self, amount: float) -> float:
        if self._display_currency == self._plan_base_currency:
            return amount
        return convert_amount(
            amount,
            self._plan_base_currency,
            self._display_currency,
            self._exchange_rates_cache,
        )

    @Slot()
    def refreshDisplayCurrencies(self) -> None:
        self._refresh_display_currencies()

    @Slot(str, "QVariant")
    def runSimulation(self, plan_id: str, params: object) -> None:
        try:
            self._clear_error()
            self._set_what_if_overrides(None)
            simulation_params = _parse_params(params)
            self._start_worker(plan_id, simulation_params)
        except Exception as exc:
            self._set_error(exc)

    @Slot(str, "QVariant", "QVariant")
    def runWhatIf(self, plan_id: str, params: object, overrides: object) -> None:
        try:
            self._clear_error()
            simulation_params = _parse_params(params)
            what_if_overrides = _parse_overrides(overrides)
            self._set_what_if_overrides(what_if_overrides or None)
            self._start_worker(plan_id, simulation_params, what_if_overrides=what_if_overrides)
        except Exception as exc:
            self._set_error(exc)

    @Slot()
    def clearError(self) -> None:
        self._clear_error()

    @Slot(str, str)
    def prefillWhatIfOverride(self, entry_id: str, change_json: str) -> None:
        if not entry_id or not change_json:
            return
        self.whatIfPrefillRequested.emit(entry_id, change_json)

    @Slot(str)
    def exportCsv(self, file_path: str) -> None:
        self._start_export(file_path, ExportFormat.CSV)

    @Slot(str, str)
    def exportPdf(self, file_path: str, plan_name: str) -> None:
        self.exportExecutivePdf(file_path, plan_name, None)

    @Slot(str, str, "QVariant")
    def exportExecutivePdf(self, file_path: str, plan_name: str, overrides: object) -> None:
        try:
            parsed_overrides: dict[str, dict[str, object]] | None = None
            if overrides is not None:
                raw = coerce_mapping(overrides, label="What-if overrides")
                if raw:
                    parsed_overrides = cast(dict[str, dict[str, object]], raw)
            self._start_export(
                file_path,
                ExportFormat.PDF,
                plan_name=plan_name,
                overrides=parsed_overrides,
            )
        except Exception as exc:
            self._set_error(exc)

    @Slot()
    def clearResult(self) -> None:
        if self._result is None:
            return
        self._result = None
        self._set_what_if_overrides(None)
        self._snapshot_model.reset([])
        if self._suggestions_vm is not None:
            self._suggestions_vm.clear()
        self.resultChanged.emit()

    @Slot(str)
    def fetchLiveRates(self, base_currency: str) -> None:
        try:
            self._clear_error()
            if not _is_live_rates_enabled():
                self._set_error(_LIVE_RATES_DISABLED_MSG)
                return
            if self._is_fetching_rates:
                return
            if not base_currency:
                self._set_error("Base currency is required to fetch live exchange rates.")
                return
            if not can_fetch_live_rates():
                if is_daily_fetch_limit_reached():
                    self._set_error(_LIVE_RATES_DAILY_LIMIT_MSG)
                else:
                    seconds = seconds_until_next_fetch()
                    if seconds < 60:
                        self._set_error(_LIVE_RATES_COOLDOWN_SECONDS_MSG.format(seconds=seconds))
                    else:
                        minutes = max(1, math.ceil(seconds / 60))
                        self._set_error(_LIVE_RATES_COOLDOWN_MINUTES_MSG.format(minutes=minutes))
                return

            symbols = [code for code in COMMON_CURRENCIES if code != base_currency]
            self._is_fetching_rates = True
            self.isFetchingRatesChanged.emit()
            worker = FetchRatesWorker(
                self._exchange_rate_repo,
                base_currency,
                symbols,
            )
            worker.signals.finished.connect(self._on_rates_fetched)
            worker.signals.error.connect(self._on_rates_error)
            self._fetch_rates_worker = worker
            QThreadPool.globalInstance().start(worker)
        except Exception as exc:
            self._set_error(exc)

    def _set_what_if_overrides(self, overrides: dict[str, dict[str, object]] | None) -> None:
        normalized = overrides or None
        if self._what_if_overrides == normalized:
            return
        self._what_if_overrides = normalized
        self.isScenarioResultChanged.emit()

    def _start_worker(
        self,
        plan_id: str,
        params: SimulationParams,
        *,
        what_if_overrides: dict[str, dict[str, object]] | None = None,
    ) -> None:
        self._is_running = True
        self.isRunningChanged.emit()
        worker = SimulationWorker(
            self._entry_repo,
            self._exchange_rate_repo,
            plan_id,
            params,
            what_if_overrides=what_if_overrides,
        )
        worker.signals.finished.connect(self._on_result)
        worker.signals.error.connect(self._on_error)
        self._worker = worker
        QThreadPool.globalInstance().start(worker)

    def _on_result(self, result: dict[str, Any]) -> None:
        self._worker = None
        self._result = result
        self._snapshot_model.reset(_parse_monthly_snapshots(result))
        self._is_running = False
        self._clear_error()
        if self._suggestions_vm is not None and self._what_if_overrides is None:
            plan_id = result.get("plan_id")
            if isinstance(plan_id, str) and plan_id:
                self._suggestions_vm.refreshForPlan(plan_id, result)
        self.resultChanged.emit()
        self.isRunningChanged.emit()

    def _on_error(self, message: str) -> None:
        self._worker = None
        self._is_running = False
        self._set_error(message)
        self.isRunningChanged.emit()

    def _on_rates_fetched(self, rates: dict[str, float]) -> None:
        del rates
        self._fetch_rates_worker = None
        self._is_fetching_rates = False
        self.isFetchingRatesChanged.emit()
        self._refresh_display_currencies()
        self.liveRatesFetched.emit()

    def _refresh_display_currencies(self) -> None:
        rates = self._exchange_rate_repo.get_all()
        self._exchange_rates_cache = rates
        currencies = display_currencies(rates, base_currency=self._plan_base_currency)
        changed = currencies != self._display_currencies
        self._display_currencies = currencies
        if self._display_currency not in self._display_currencies:
            self._display_currency = self._plan_base_currency
            self.displayCurrencyChanged.emit()
        if changed:
            self.displayCurrenciesChanged.emit()
        if self._active_plan_id:
            saved = QSettings().value(_display_currency_settings_key(self._active_plan_id))
            if (
                isinstance(saved, str)
                and saved in self._display_currencies
                and saved != self._display_currency
            ):
                self._display_currency = saved
                self.displayCurrencyChanged.emit()

    def _on_rates_error(self, message: str) -> None:
        self._fetch_rates_worker = None
        self._is_fetching_rates = False
        self._set_error(message)
        self.isFetchingRatesChanged.emit()

    def _start_export(
        self,
        file_path: str,
        export_format: ExportFormat,
        *,
        plan_name: str = "",
        overrides: dict[str, dict[str, object]] | None = None,
    ) -> None:
        try:
            if self._result is None:
                self._set_error(_NO_RESULT_MSG)
                return
            self._clear_error()
            plan_id = self._result.get("plan_id")
            if not isinstance(plan_id, str) or not plan_id:
                plan_id = self._active_plan_id
            if export_format is ExportFormat.PDF and plan_id:
                worker = ExportWorker(
                    self._result,
                    file_path,
                    export_format,
                    plan_name=plan_name,
                    display_currency=self._display_currency,
                    exchange_rates=self._exchange_rates_cache,
                    plan_id=plan_id,
                    entry_repo=self._entry_repo,
                    exchange_rate_repo=self._exchange_rate_repo,
                    overrides=overrides,
                    app_version=app_version(),
                )
            else:
                worker = ExportWorker(
                    self._result,
                    file_path,
                    export_format,
                    plan_name=plan_name,
                    display_currency=self._display_currency,
                    exchange_rates=self._exchange_rates_cache,
                    app_version=app_version(),
                )
            worker.signals.finished.connect(self._on_export_finished)
            worker.signals.error.connect(self._on_export_error)
            self._export_worker = worker
            QThreadPool.globalInstance().start(worker)
        except Exception as exc:
            self._set_error(exc)

    def _on_export_finished(self) -> None:
        self._export_worker = None
        self.exportSucceeded.emit()

    def _on_export_error(self, message: str) -> None:
        self._export_worker = None
        self._set_error(message)

    @Slot()
    def retranslate(self) -> None:
        self._errors.retranslate()

    def _set_error(self, exc: BaseException | str) -> None:
        if isinstance(exc, BaseException):
            self._errors.set_from_exception(exc)
            return
        self._errors.set(exc)

    def _clear_error(self) -> None:
        if not self._errors.clear():
            return
        self.errorChanged.emit()
