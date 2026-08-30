from __future__ import annotations

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest
from PySide6.QtCore import QCoreApplication, QSettings

from src.app.identity import ORGANIZATION_NAME
from src.app.user_manual import manual_qrc_path
from src.app.viewmodels.settings_vm import SettingsViewModel
from src.integrations.exchange_rate_fetcher import (
    _DAILY_FETCH_COUNT_KEY,
    _DAILY_FETCH_DATE_KEY,
    _LAST_FETCH_AT_KEY,
    _USE_MOCK_RATES_KEY,
    configure_dev_mode,
    record_successful_fetch,
)

_DARK_MODE_KEY = "darkMode"
_LANGUAGE_KEY = "language"
_LIVE_RATES_ENABLED_KEY = "exchange_rate_api_enabled"
_CLOUD_RECEIPT_OCR_KEY = "receipt_ocr_cloud_enabled"


@pytest.fixture
def settings_vm(qt_app: object) -> SettingsViewModel:
    _ = qt_app
    QCoreApplication.setOrganizationName(ORGANIZATION_NAME)
    QCoreApplication.setApplicationName("CashFlowPlannerDesktopTest")
    settings = QSettings()
    settings.remove(_DARK_MODE_KEY)
    settings.remove(_LANGUAGE_KEY)
    settings.remove(_LIVE_RATES_ENABLED_KEY)
    settings.remove(_CLOUD_RECEIPT_OCR_KEY)
    settings.remove(_LAST_FETCH_AT_KEY)
    settings.remove(_DAILY_FETCH_DATE_KEY)
    settings.remove(_DAILY_FETCH_COUNT_KEY)
    settings.remove(_USE_MOCK_RATES_KEY)
    settings.sync()
    configure_dev_mode(enabled=False)
    return SettingsViewModel()


@pytest.fixture(autouse=True)
def reset_dev_mode() -> None:
    configure_dev_mode(enabled=False)
    yield
    configure_dev_mode(enabled=False)


@pytest.mark.integration
def test_dark_mode_defaults_to_false(settings_vm: SettingsViewModel) -> None:
    assert settings_vm.darkMode is False


@pytest.mark.integration
def test_language_defaults_to_english(settings_vm: SettingsViewModel) -> None:
    assert settings_vm.language == "en"


@pytest.mark.integration
def test_set_language_persists_to_qsettings(settings_vm: SettingsViewModel) -> None:
    settings_vm.setLanguage("fr")

    assert settings_vm.language == "fr"
    assert QSettings().value(_LANGUAGE_KEY) == "fr"

    reloaded = SettingsViewModel()
    assert reloaded.language == "fr"


@pytest.mark.integration
def test_set_dark_mode_persists_to_qsettings(settings_vm: SettingsViewModel) -> None:
    settings_vm.setDarkMode(True)

    assert settings_vm.darkMode is True
    assert QSettings().value(_DARK_MODE_KEY) is True

    reloaded = SettingsViewModel()
    assert reloaded.darkMode is True


@pytest.mark.integration
def test_live_rates_defaults_to_false(settings_vm: SettingsViewModel) -> None:
    assert settings_vm.liveRatesEnabled is False


@pytest.mark.integration
def test_cloud_receipt_ocr_defaults_to_false(settings_vm: SettingsViewModel) -> None:
    assert settings_vm.cloudReceiptOcrEnabled is False


@pytest.mark.integration
def test_set_cloud_receipt_ocr_enabled_persists_to_qsettings(
    settings_vm: SettingsViewModel,
) -> None:
    settings_vm.setCloudReceiptOcrEnabled(True)

    assert settings_vm.cloudReceiptOcrEnabled is True
    assert QSettings().value(_CLOUD_RECEIPT_OCR_KEY) is True

    reloaded = SettingsViewModel()
    assert reloaded.cloudReceiptOcrEnabled is True


@pytest.mark.integration
def test_set_live_rates_enabled_persists_to_qsettings(settings_vm: SettingsViewModel) -> None:
    settings_vm.setLiveRatesEnabled(True)

    assert settings_vm.liveRatesEnabled is True
    assert QSettings().value(_LIVE_RATES_ENABLED_KEY) is True

    reloaded = SettingsViewModel()
    assert reloaded.liveRatesEnabled is True


@pytest.mark.integration
def test_live_rates_fetch_available_defaults_to_true(settings_vm: SettingsViewModel) -> None:
    assert settings_vm.liveRatesFetchAvailable is True
    assert settings_vm.secondsUntilLiveRatesFetch == 0
    assert settings_vm.liveRatesDailyLimitReached is False


@pytest.mark.integration
def test_refresh_live_rates_cooldown_after_recent_fetch(
    settings_vm: SettingsViewModel,
) -> None:
    recent_fetch = datetime.now().replace(microsecond=0)
    record_successful_fetch(now=recent_fetch)

    settings_vm.refreshLiveRatesCooldown()

    assert settings_vm.liveRatesFetchAvailable is False
    assert settings_vm.liveRatesDailyLimitReached is False
    assert settings_vm.secondsUntilLiveRatesFetch >= 1


@pytest.mark.integration
def test_dev_mode_disabled_by_default(settings_vm: SettingsViewModel) -> None:
    assert settings_vm.devModeEnabled is False
    assert settings_vm.useMockExchangeRates is False


@pytest.mark.integration
def test_use_mock_exchange_rates_when_dev_mode_enabled(
    settings_vm: SettingsViewModel,
) -> None:
    configure_dev_mode(enabled=True)
    reloaded = SettingsViewModel()

    assert reloaded.devModeEnabled is True
    assert reloaded.useMockExchangeRates is False

    reloaded.setUseMockExchangeRates(True)

    assert reloaded.useMockExchangeRates is True
    assert QSettings().value(_USE_MOCK_RATES_KEY) is True

    persisted = SettingsViewModel()
    assert persisted.useMockExchangeRates is True


@pytest.mark.integration
def test_set_use_mock_exchange_rates_ignored_without_dev_mode(
    settings_vm: SettingsViewModel,
) -> None:
    settings_vm.setUseMockExchangeRates(True)

    assert settings_vm.useMockExchangeRates is False
    assert QSettings().value(_USE_MOCK_RATES_KEY) is None


@pytest.mark.integration
def test_open_user_manual_sets_error_when_resource_missing(
    settings_vm: SettingsViewModel,
) -> None:
    with patch("src.app.user_manual.resolve_manual_qrc_path", return_value=None):
        settings_vm.openUserManual()

    assert settings_vm.error == "User manual is not available."


@pytest.mark.integration
def test_open_user_manual_clears_error_on_success(
    settings_vm: SettingsViewModel,
) -> None:
    import src.app.resources_rc  # noqa: F401

    settings_vm._set_error("User manual is not available.")  # noqa: SLF001

    with patch("PySide6.QtGui.QDesktopServices.openUrl", return_value=True):
        settings_vm.openUserManual()

    assert settings_vm.error == ""


@pytest.mark.integration
def test_open_user_manual_uses_active_language(
    settings_vm: SettingsViewModel,
) -> None:
    import src.app.resources_rc  # noqa: F401

    settings_vm.setLanguage("fr")

    with (
        patch("src.app.user_manual.materialize_manual_pdf") as materialize,
        patch("PySide6.QtGui.QDesktopServices.openUrl", return_value=True),
    ):
        materialize.return_value = Path("/tmp/manual.pdf")
        settings_vm.openUserManual()

    materialize.assert_called_once_with(manual_qrc_path("fr"))
