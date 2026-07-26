from __future__ import annotations

from PySide6.QtCore import Property, QObject, QSettings, Signal, Slot

from src.app.user_manual import UserManualError, open_user_manual
from src.app.viewmodels.error_support import ErrorSupport
from src.integrations.exchange_rate_fetcher import (
    can_fetch_live_rates,
    is_daily_fetch_limit_reached,
    is_dev_mode_enabled,
    seconds_until_next_fetch,
    set_use_mock_rates,
    use_mock_rates,
)

_DARK_MODE_KEY = "darkMode"
_LANGUAGE_KEY = "language"
_LIVE_RATES_ENABLED_KEY = "exchange_rate_api_enabled"


def _settings_bool(value: object, *, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes"}
    return bool(value)


class SettingsViewModel(QObject):
    """Application-level settings exposed to QML and persisted via QSettings."""

    darkModeChanged = Signal()
    languageChanged = Signal()
    liveRatesEnabledChanged = Signal()
    liveRatesFetchAvailableChanged = Signal()
    secondsUntilLiveRatesFetchChanged = Signal()
    liveRatesDailyLimitReachedChanged = Signal()
    useMockExchangeRatesChanged = Signal()
    errorChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._errors = ErrorSupport(self)
        settings = QSettings()
        self._dark_mode = _settings_bool(settings.value(_DARK_MODE_KEY), default=False)
        language = settings.value(_LANGUAGE_KEY, "en")
        self._language = language if isinstance(language, str) and language else "en"
        self._live_rates_enabled = _settings_bool(
            settings.value(_LIVE_RATES_ENABLED_KEY),
            default=False,
        )
        self._live_rates_fetch_available = can_fetch_live_rates()
        self._seconds_until_live_rates_fetch = seconds_until_next_fetch()
        self._live_rates_daily_limit_reached = is_daily_fetch_limit_reached()
        self._use_mock_exchange_rates = use_mock_rates()

    @Property(bool, notify=darkModeChanged)
    def darkMode(self) -> bool:
        return self._dark_mode

    @Property(str, notify=languageChanged)
    def language(self) -> str:
        return self._language

    @Property(bool, notify=liveRatesEnabledChanged)
    def liveRatesEnabled(self) -> bool:
        return self._live_rates_enabled

    @Property(bool, notify=liveRatesFetchAvailableChanged)
    def liveRatesFetchAvailable(self) -> bool:
        return self._live_rates_fetch_available

    @Property(int, notify=secondsUntilLiveRatesFetchChanged)
    def secondsUntilLiveRatesFetch(self) -> int:
        return self._seconds_until_live_rates_fetch

    @Property(bool, notify=liveRatesDailyLimitReachedChanged)
    def liveRatesDailyLimitReached(self) -> bool:
        return self._live_rates_daily_limit_reached

    @Property(bool, constant=True)
    def devModeEnabled(self) -> bool:
        return is_dev_mode_enabled()

    @Property(bool, notify=useMockExchangeRatesChanged)
    def useMockExchangeRates(self) -> bool:
        return self._use_mock_exchange_rates

    @Property(str, notify=errorChanged)
    def error(self) -> str:
        return self._errors.message

    @Slot()
    def openUserManual(self) -> None:
        try:
            open_user_manual(self._language)
            self._clear_error()
        except UserManualError as exc:
            self._set_error(exc)

    @Slot()
    def clearError(self) -> None:
        self._clear_error()

    @Slot()
    def refreshLiveRatesCooldown(self) -> None:
        available = can_fetch_live_rates()
        seconds_remaining = seconds_until_next_fetch()
        daily_limit_reached = is_daily_fetch_limit_reached()
        if self._live_rates_fetch_available != available:
            self._live_rates_fetch_available = available
            self.liveRatesFetchAvailableChanged.emit()
        if self._seconds_until_live_rates_fetch != seconds_remaining:
            self._seconds_until_live_rates_fetch = seconds_remaining
            self.secondsUntilLiveRatesFetchChanged.emit()
        if self._live_rates_daily_limit_reached != daily_limit_reached:
            self._live_rates_daily_limit_reached = daily_limit_reached
            self.liveRatesDailyLimitReachedChanged.emit()

    @Slot(bool)
    def setDarkMode(self, enabled: bool) -> None:
        if self._dark_mode == enabled:
            return
        self._dark_mode = enabled
        QSettings().setValue(_DARK_MODE_KEY, enabled)
        self.darkModeChanged.emit()

    @Slot(str)
    def setLanguage(self, lang: str) -> None:
        if lang == self._language:
            return
        self._language = lang
        QSettings().setValue(_LANGUAGE_KEY, lang)
        self.languageChanged.emit()

    @Slot(bool)
    def setLiveRatesEnabled(self, enabled: bool) -> None:
        if self._live_rates_enabled == enabled:
            return
        self._live_rates_enabled = enabled
        QSettings().setValue(_LIVE_RATES_ENABLED_KEY, enabled)
        self.liveRatesEnabledChanged.emit()

    @Slot(bool)
    def setUseMockExchangeRates(self, enabled: bool) -> None:
        if not is_dev_mode_enabled():
            return
        set_use_mock_rates(enabled)
        if self._use_mock_exchange_rates == enabled:
            return
        self._use_mock_exchange_rates = enabled
        self.useMockExchangeRatesChanged.emit()

    def _set_error(self, exc: BaseException | str) -> None:
        if isinstance(exc, BaseException):
            self._errors.set_from_exception(exc)
            return
        self._errors.set(exc)

    def _clear_error(self) -> None:
        if not self._errors.clear():
            return
        self.errorChanged.emit()
