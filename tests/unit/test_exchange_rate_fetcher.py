from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import httpx
import pytest
from PySide6.QtCore import QCoreApplication, QSettings

from src.app.identity import ORGANIZATION_NAME
from src.domain.exceptions import FetchRatesError
from src.integrations.exchange_rate_fetcher import (
    _API_TIMEOUT_KEY,
    _API_URL_KEY,
    _DAILY_FETCH_COUNT_KEY,
    _DAILY_FETCH_DATE_KEY,
    _LAST_FETCH_AT_KEY,
    _MAX_DAILY_FETCHES,
    _USE_MOCK_RATES_KEY,
    can_fetch_live_rates,
    configure_dev_mode,
    fetch_rates,
    is_daily_fetch_limit_reached,
    record_successful_fetch,
    seconds_until_next_fetch,
    set_use_mock_rates,
    use_mock_rates,
)

_V6_API_RESPONSE = {
    "result": "success",
    "base_code": "USD",
    "conversion_rates": {
        "USD": 1,
        "EUR": 0.8808,
        "GBP": 0.7597,
    },
}

_API_RESPONSE = {
    "success": True,
    "base": "USD",
    "date": "2026-06-25",
    "rates": {"EUR": 0.85, "GBP": 0.75},
}


@pytest.fixture
def qsettings_env(qt_app: object) -> None:
    _ = qt_app
    QCoreApplication.setOrganizationName(ORGANIZATION_NAME)
    QCoreApplication.setApplicationName("CashFlowPlannerDesktopFetcherTest")
    settings = QSettings()
    settings.remove(_API_URL_KEY)
    settings.remove(_API_TIMEOUT_KEY)
    settings.remove(_LAST_FETCH_AT_KEY)
    settings.remove(_DAILY_FETCH_DATE_KEY)
    settings.remove(_DAILY_FETCH_COUNT_KEY)
    settings.remove(_USE_MOCK_RATES_KEY)
    settings.sync()
    configure_dev_mode(enabled=False)


@pytest.fixture(autouse=True)
def reset_dev_mode() -> None:
    configure_dev_mode(enabled=False)
    yield
    configure_dev_mode(enabled=False)


def _use_query_param_api_url() -> None:
    QSettings().setValue(_API_URL_KEY, "https://api.exchangerate.host/latest")


@pytest.mark.unit
def test_fetch_rates_returns_requested_symbols(
    qsettings_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _use_query_param_api_url()
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.json.return_value = _API_RESPONSE

    monkeypatch.setattr(
        "src.integrations.exchange_rate_fetcher.httpx.get",
        lambda url, params, timeout: response,
    )

    rates = fetch_rates("USD", ["EUR", "GBP"])

    assert "EUR" in rates
    assert "GBP" in rates
    assert rates["EUR"] == 0.85
    assert rates["GBP"] == 0.75


@pytest.mark.unit
def test_fetch_rates_raises_on_non_200(
    qsettings_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _use_query_param_api_url()
    response = MagicMock(spec=httpx.Response)
    response.status_code = 503
    response.json.return_value = {}

    monkeypatch.setattr(
        "src.integrations.exchange_rate_fetcher.httpx.get",
        lambda url, params, timeout: response,
    )

    with pytest.raises(FetchRatesError, match="HTTP 503"):
        fetch_rates("USD", ["EUR"])


@pytest.mark.unit
def test_fetch_rates_raises_on_unreachable_url(
    qsettings_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    QSettings().setValue(_API_URL_KEY, "http://127.0.0.1:1/latest")

    def _raise_connection_error(url: str, params: dict[str, str], timeout: float) -> httpx.Response:
        raise httpx.ConnectError("Connection refused")

    monkeypatch.setattr("src.integrations.exchange_rate_fetcher.httpx.get", _raise_connection_error)

    with pytest.raises(FetchRatesError):
        fetch_rates("USD", ["EUR"])


@pytest.mark.unit
def test_fetch_rates_uses_open_access_url_by_default(
    qsettings_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.json.return_value = _V6_API_RESPONSE
    captured: dict[str, str] = {}

    def _capture_get(url: str, params: dict[str, str], timeout: float) -> httpx.Response:
        captured["url"] = url
        captured["params"] = str(params)
        return response

    monkeypatch.setattr("src.integrations.exchange_rate_fetcher.httpx.get", _capture_get)

    rates = fetch_rates("USD", ["EUR", "GBP"])

    assert rates == {"EUR": 0.8808, "GBP": 0.7597}
    assert captured["url"] == "https://open.er-api.com/v6/latest/USD"
    assert captured["params"] == "{}"


@pytest.mark.unit
def test_fetch_rates_falls_back_to_legacy_rates_field(
    qsettings_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    QSettings().setValue(_API_URL_KEY, "https://api.exchangerate-api.com/v4/latest/USD")
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.json.return_value = {
        "base": "USD",
        "date": "2026-06-25",
        "rates": {"USD": 1, "EUR": 0.881, "GBP": 0.76},
    }

    monkeypatch.setattr(
        "src.integrations.exchange_rate_fetcher.httpx.get",
        lambda url, params, timeout: response,
    )

    rates = fetch_rates("USD", ["EUR", "GBP"])

    assert rates == {"EUR": 0.881, "GBP": 0.76}


@pytest.mark.unit
def test_can_fetch_live_rates_when_never_fetched() -> None:
    now = datetime(2026, 6, 25, 12, 0)
    assert can_fetch_live_rates(now=now, last_fetch_at=None, daily_fetch_count=0) is True


@pytest.mark.unit
def test_can_fetch_live_rates_false_during_minute_cooldown() -> None:
    now = datetime(2026, 6, 25, 12, 0, 30)
    last_fetch_at = datetime(2026, 6, 25, 12, 0)
    assert can_fetch_live_rates(now=now, last_fetch_at=last_fetch_at, daily_fetch_count=1) is False


@pytest.mark.unit
def test_can_fetch_live_rates_true_after_minute_cooldown() -> None:
    now = datetime(2026, 6, 25, 12, 1, 1)
    last_fetch_at = datetime(2026, 6, 25, 12, 0)
    assert can_fetch_live_rates(now=now, last_fetch_at=last_fetch_at, daily_fetch_count=1) is True


@pytest.mark.unit
def test_can_fetch_live_rates_false_when_daily_limit_reached() -> None:
    now = datetime(2026, 6, 25, 15, 30)
    last_fetch_at = datetime(2026, 6, 25, 14, 0)
    assert (
        can_fetch_live_rates(
            now=now,
            last_fetch_at=last_fetch_at,
            daily_fetch_count=_MAX_DAILY_FETCHES,
        )
        is False
    )


@pytest.mark.unit
def test_seconds_until_next_fetch_zero_when_available() -> None:
    now = datetime(2026, 6, 25, 15, 30)
    assert seconds_until_next_fetch(now=now, last_fetch_at=None, daily_fetch_count=0) == 0


@pytest.mark.unit
def test_seconds_until_next_fetch_counts_cooldown_seconds() -> None:
    now = datetime(2026, 6, 25, 12, 0, 20)
    last_fetch_at = datetime(2026, 6, 25, 12, 0)
    assert seconds_until_next_fetch(now=now, last_fetch_at=last_fetch_at, daily_fetch_count=1) == 40


@pytest.mark.unit
def test_seconds_until_next_fetch_counts_seconds_until_midnight_for_daily_limit() -> None:
    now = datetime(2026, 6, 25, 23, 45)
    assert (
        seconds_until_next_fetch(
            now=now,
            last_fetch_at=datetime(2026, 6, 25, 22, 0),
            daily_fetch_count=_MAX_DAILY_FETCHES,
        )
        == 900
    )


@pytest.mark.unit
def test_is_daily_fetch_limit_reached() -> None:
    assert is_daily_fetch_limit_reached(daily_fetch_count=_MAX_DAILY_FETCHES) is True
    assert is_daily_fetch_limit_reached(daily_fetch_count=_MAX_DAILY_FETCHES - 1) is False


@pytest.mark.unit
def test_can_fetch_live_rates_true_when_mock_enabled(qsettings_env: None) -> None:
    configure_dev_mode(enabled=True)
    set_use_mock_rates(True)
    now = datetime(2026, 6, 25, 12, 0, 10)
    last_fetch_at = datetime(2026, 6, 25, 12, 0)

    assert can_fetch_live_rates(now=now, last_fetch_at=last_fetch_at, daily_fetch_count=10) is True


@pytest.mark.unit
def test_seconds_until_next_fetch_zero_when_mock_enabled(qsettings_env: None) -> None:
    configure_dev_mode(enabled=True)
    set_use_mock_rates(True)
    now = datetime(2026, 6, 25, 15, 30)

    assert (
        seconds_until_next_fetch(
            now=now,
            last_fetch_at=datetime(2026, 6, 25, 15, 29),
            daily_fetch_count=10,
        )
        == 0
    )


@pytest.mark.unit
def test_record_successful_fetch_persists_timestamp_and_count(qsettings_env: None) -> None:
    fetched_at = datetime(2026, 6, 25, 12, 34, 56)
    record_successful_fetch(now=fetched_at)

    assert QSettings().value(_LAST_FETCH_AT_KEY) == "2026-06-25T12:34:56"
    assert QSettings().value(_DAILY_FETCH_DATE_KEY) == "2026-06-25"
    assert QSettings().value(_DAILY_FETCH_COUNT_KEY) == 1
    assert (
        can_fetch_live_rates(
            now=fetched_at,
            last_fetch_at=fetched_at,
            daily_fetch_count=1,
        )
        is False
    )


@pytest.mark.unit
def test_fetch_rates_uses_mock_when_dev_mode_and_setting_enabled(
    qsettings_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_dev_mode(enabled=True)
    set_use_mock_rates(True)

    def _should_not_call_api(url: str, params: dict[str, str], timeout: float) -> httpx.Response:
        msg = "Real API must not be called when mock rates are enabled"
        raise AssertionError(msg)

    monkeypatch.setattr("src.integrations.exchange_rate_fetcher.httpx.get", _should_not_call_api)

    rates = fetch_rates("USD", ["EUR", "GBP"])

    assert rates == {"EUR": 0.92, "GBP": 0.79}


@pytest.mark.unit
def test_fetch_rates_ignores_mock_setting_without_dev_mode(
    qsettings_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_use_mock_rates(True)
    _use_query_param_api_url()
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.json.return_value = _API_RESPONSE

    monkeypatch.setattr(
        "src.integrations.exchange_rate_fetcher.httpx.get",
        lambda url, params, timeout: response,
    )

    rates = fetch_rates("USD", ["EUR", "GBP"])

    assert rates == {"EUR": 0.85, "GBP": 0.75}


@pytest.mark.unit
def test_use_mock_rates_false_without_dev_mode(qsettings_env: None) -> None:
    set_use_mock_rates(True)

    assert use_mock_rates() is False


@pytest.mark.unit
def test_set_use_mock_rates_ignored_without_dev_mode(qsettings_env: None) -> None:
    configure_dev_mode(enabled=False)
    set_use_mock_rates(True)

    assert QSettings().value(_USE_MOCK_RATES_KEY) is None


@pytest.mark.unit
def test_fetch_mock_rates_raises_for_unknown_base(qsettings_env: None) -> None:
    configure_dev_mode(enabled=True)
    set_use_mock_rates(True)

    with pytest.raises(FetchRatesError, match="not defined for base currency"):
        fetch_rates("XXX", ["USD"])


@pytest.mark.unit
def test_fetch_mock_rates_supports_central_asia_base(qsettings_env: None) -> None:
    configure_dev_mode(enabled=True)
    set_use_mock_rates(True)

    rates = fetch_rates("KZT", ["USD", "UZS"])

    assert rates["USD"] == pytest.approx(1.0 / 450.0)
    assert rates["UZS"] == pytest.approx(12500.0 / 450.0)
