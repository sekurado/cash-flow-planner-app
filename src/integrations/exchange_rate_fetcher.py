from __future__ import annotations

import math
from datetime import date, datetime, time, timedelta

import httpx
from PySide6.QtCore import QObject, QRunnable, QSettings, Signal

from src.data.repositories.exchange_rate_repo import (
    AbstractExchangeRateRepository,
    ExchangeRateUpsertDto,
    SqliteExchangeRateRepository,
)
from src.domain.exceptions import FetchRatesError

DEFAULT_API_URL = "https://open.er-api.com/v6/latest/{base}"
DEFAULT_TIMEOUT = 10.0
_MIN_FETCH_INTERVAL = timedelta(minutes=1)
_MAX_DAILY_FETCHES = 10
_API_URL_KEY = "exchange_rate_api_url"
_API_TIMEOUT_KEY = "exchange_rate_api_timeout"
_LAST_FETCH_AT_KEY = "exchange_rate_last_fetch_at"
_DAILY_FETCH_DATE_KEY = "exchange_rate_daily_fetch_date"
_DAILY_FETCH_COUNT_KEY = "exchange_rate_daily_fetch_count"
_USE_MOCK_RATES_KEY = "exchange_rate_use_mock"

# Approximate units of each currency per 1 USD (dev mock only).
_MOCK_USD_RATES: dict[str, float] = {
    "AED": 3.67,
    "AMD": 390.0,
    "ARS": 900.0,
    "AUD": 1.52,
    "AZN": 1.70,
    "BDT": 110.0,
    "BGN": 1.80,
    "BHD": 0.38,
    "BRL": 5.0,
    "CAD": 1.36,
    "CHF": 0.88,
    "CLP": 950.0,
    "CNY": 7.25,
    "COP": 4100.0,
    "CZK": 23.0,
    "DKK": 6.85,
    "EGP": 48.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "GEL": 2.65,
    "GHS": 15.0,
    "HKD": 7.80,
    "HUF": 360.0,
    "IDR": 15800.0,
    "ILS": 3.65,
    "INR": 83.0,
    "JOD": 0.71,
    "JPY": 149.5,
    "KES": 130.0,
    "KGS": 89.0,
    "KRW": 1350.0,
    "KWD": 0.31,
    "KZT": 450.0,
    "LKR": 300.0,
    "MAD": 10.0,
    "MXN": 17.0,
    "MYR": 4.75,
    "NGN": 1550.0,
    "NOK": 10.6,
    "NZD": 1.65,
    "OMR": 0.38,
    "PEN": 3.75,
    "PHP": 56.0,
    "PKR": 278.0,
    "PLN": 4.0,
    "QAR": 3.64,
    "RON": 4.6,
    "RSD": 108.0,
    "RUB": 92.0,
    "SAR": 3.75,
    "SEK": 10.5,
    "SGD": 1.35,
    "THB": 36.0,
    "TJS": 10.9,
    "TMT": 3.50,
    "TRY": 32.0,
    "TWD": 32.0,
    "UAH": 41.0,
    "USD": 1.0,
    "UYU": 40.0,
    "UZS": 12500.0,
    "VND": 25000.0,
    "ZAR": 18.5,
}

_dev_mode_enabled = False


def _parse_api_url(value: object) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return DEFAULT_API_URL


def _parse_timeout(value: object) -> float:
    if value is None:
        return DEFAULT_TIMEOUT
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        return float(value)
    return DEFAULT_TIMEOUT


def _settings_bool(value: object, *, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes"}
    return bool(value)


def configure_dev_mode(*, enabled: bool) -> None:
    """Enable dev-only settings such as the mock exchange-rate provider."""
    global _dev_mode_enabled
    _dev_mode_enabled = enabled


def is_dev_mode_enabled() -> bool:
    return _dev_mode_enabled


def use_mock_rates() -> bool:
    if not _dev_mode_enabled:
        return False
    return _settings_bool(QSettings().value(_USE_MOCK_RATES_KEY), default=False)


def set_use_mock_rates(enabled: bool) -> None:
    if not _dev_mode_enabled:
        return
    QSettings().setValue(_USE_MOCK_RATES_KEY, enabled)


def _parse_iso_date(value: object) -> date | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def _parse_last_fetch_at(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.strip())
    except ValueError:
        return None


def _parse_daily_fetch_count(value: object) -> int:
    if value is None:
        return 0
    if isinstance(value, int):
        return max(0, value)
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return 0


def get_last_fetch_at() -> datetime | None:
    return _parse_last_fetch_at(QSettings().value(_LAST_FETCH_AT_KEY))


def _get_daily_fetch_count(*, today: date) -> int:
    settings = QSettings()
    stored_date = _parse_iso_date(settings.value(_DAILY_FETCH_DATE_KEY))
    if stored_date != today:
        return 0
    return _parse_daily_fetch_count(settings.value(_DAILY_FETCH_COUNT_KEY))


def record_successful_fetch(*, now: datetime | None = None) -> None:
    resolved_now = datetime.now() if now is None else now
    today = resolved_now.date()
    settings = QSettings()
    daily_count = _get_daily_fetch_count(today=today)
    settings.setValue(_LAST_FETCH_AT_KEY, resolved_now.isoformat(timespec="seconds"))
    settings.setValue(_DAILY_FETCH_DATE_KEY, today.isoformat())
    settings.setValue(_DAILY_FETCH_COUNT_KEY, daily_count + 1)


def is_daily_fetch_limit_reached(
    *,
    now: datetime | None = None,
    daily_fetch_count: int | None = None,
) -> bool:
    if use_mock_rates():
        return False
    resolved_now = datetime.now() if now is None else now
    resolved_count = (
        _get_daily_fetch_count(today=resolved_now.date())
        if daily_fetch_count is None
        else daily_fetch_count
    )
    return resolved_count >= _MAX_DAILY_FETCHES


def can_fetch_live_rates(
    *,
    now: datetime | None = None,
    last_fetch_at: datetime | None = None,
    daily_fetch_count: int | None = None,
) -> bool:
    if use_mock_rates():
        return True
    resolved_now = datetime.now() if now is None else now
    if is_daily_fetch_limit_reached(now=resolved_now, daily_fetch_count=daily_fetch_count):
        return False

    resolved_last_fetch_at = get_last_fetch_at() if last_fetch_at is None else last_fetch_at
    if resolved_last_fetch_at is None:
        return True
    elapsed = resolved_now - resolved_last_fetch_at
    return elapsed >= _MIN_FETCH_INTERVAL


def seconds_until_next_fetch(
    *,
    now: datetime | None = None,
    last_fetch_at: datetime | None = None,
    daily_fetch_count: int | None = None,
) -> int:
    if use_mock_rates():
        return 0
    resolved_now = datetime.now() if now is None else now
    if can_fetch_live_rates(
        now=resolved_now,
        last_fetch_at=last_fetch_at,
        daily_fetch_count=daily_fetch_count,
    ):
        return 0

    if is_daily_fetch_limit_reached(now=resolved_now, daily_fetch_count=daily_fetch_count):
        next_midnight = datetime.combine(resolved_now.date() + timedelta(days=1), time.min)
        remaining_seconds = (next_midnight - resolved_now).total_seconds()
        return max(1, math.ceil(remaining_seconds))

    resolved_last_fetch_at = get_last_fetch_at() if last_fetch_at is None else last_fetch_at
    if resolved_last_fetch_at is None:
        return 0
    next_allowed = resolved_last_fetch_at + _MIN_FETCH_INTERVAL
    remaining_seconds = (next_allowed - resolved_now).total_seconds()
    return max(1, math.ceil(remaining_seconds))


def _read_api_settings() -> tuple[str, float]:
    settings = QSettings()
    return (
        _parse_api_url(settings.value(_API_URL_KEY)),
        _parse_timeout(settings.value(_API_TIMEOUT_KEY)),
    )


def _api_rate_to_normalizer_rate(api_rate: float) -> float:
    """Convert a base→symbol API rate into a symbol→base normalizer rate."""
    if api_rate == 0:
        msg = "Exchange rate API returned a zero rate"
        raise FetchRatesError(msg)
    return 1.0 / api_rate


def _build_request(
    base: str,
    symbols: list[str],
    api_url: str,
) -> tuple[str, dict[str, str]]:
    request_url = api_url
    if "{base}" in request_url:
        request_url = request_url.replace("{base}", base)
        return request_url, {}

    normalized = request_url.rstrip("/")
    if normalized.upper().endswith(f"/{base.upper()}"):
        return request_url, {}

    params: dict[str, str] = {"base": base}
    if symbols:
        params["symbols"] = ",".join(symbols)
    return request_url, params


def _fetch_mock_rates(base: str, symbols: list[str]) -> dict[str, float]:
    if base not in _MOCK_USD_RATES:
        msg = f"Mock exchange rates are not defined for base currency {base}"
        raise FetchRatesError(msg)

    base_per_usd = _MOCK_USD_RATES[base]
    requested = symbols if symbols else list(_MOCK_USD_RATES)
    rates: dict[str, float] = {}
    for symbol in requested:
        if symbol == base:
            continue
        symbol_per_usd = _MOCK_USD_RATES.get(symbol)
        if symbol_per_usd is None:
            joined = symbol
            msg = f"Mock exchange rates are missing symbols: {joined}"
            raise FetchRatesError(msg)
        rates[symbol] = symbol_per_usd / base_per_usd
    return rates


def _fetch_rates_from_api(base: str, symbols: list[str]) -> dict[str, float]:
    api_url, timeout = _read_api_settings()
    request_url, params = _build_request(base, symbols, api_url)

    try:
        response = httpx.get(request_url, params=params, timeout=timeout)
    except httpx.HTTPError as exc:
        raise FetchRatesError(str(exc)) from exc

    if response.status_code != 200:
        msg = f"Exchange rate API returned HTTP {response.status_code}"
        raise FetchRatesError(msg)

    try:
        data = response.json()
    except ValueError as exc:
        raise FetchRatesError("Exchange rate API returned invalid JSON") from exc

    if data.get("result") == "error":
        error_type = data.get("error-type", "Unknown API error")
        raise FetchRatesError(str(error_type))

    if data.get("success") is False:
        error_info = data.get("error", {})
        if isinstance(error_info, dict):
            message = error_info.get("info", "Unknown API error")
        else:
            message = "Unknown API error"
        raise FetchRatesError(str(message))

    parsed_rates = _parse_rates_payload(data)

    if symbols:
        return {symbol: parsed_rates[symbol] for symbol in symbols if symbol in parsed_rates}

    return parsed_rates


def fetch_rates(base: str, symbols: list[str]) -> dict[str, float]:
    """Fetch latest exchange rates for the given symbols relative to base.

    Returns ``{currency_code: rate_from_base}`` as returned by the API, or raises
    ``FetchRatesError`` on network errors or non-200 responses. In dev mode, may
    return prepared mock rates when that option is enabled in settings.
    """
    if use_mock_rates():
        return _fetch_mock_rates(base, symbols)
    return _fetch_rates_from_api(base, symbols)


def _parse_rates_payload(data: dict[str, object]) -> dict[str, float]:
    rates_raw = data.get("conversion_rates")
    if not isinstance(rates_raw, dict):
        rates_raw = data.get("rates")
    if not isinstance(rates_raw, dict):
        msg = "Exchange rate API response is missing conversion rates"
        raise FetchRatesError(msg)

    parsed_rates: dict[str, float] = {}
    for symbol, rate in rates_raw.items():
        if not isinstance(symbol, str) or not isinstance(rate, (int, float)):
            continue
        parsed_rates[symbol] = float(rate)

    return parsed_rates


class FetchRatesWorkerSignals(QObject):
    finished = Signal(dict)
    error = Signal(str)


class FetchRatesWorker(QRunnable):
    """Fetches live exchange rates off the main thread and persists them to the database."""

    def __init__(
        self,
        exchange_rate_repo: AbstractExchangeRateRepository,
        base: str,
        symbols: list[str],
    ) -> None:
        super().__init__()
        self._exchange_rate_repo = exchange_rate_repo
        self._base = base
        self._symbols = symbols
        self.signals = FetchRatesWorkerSignals()

    def run(self) -> None:
        try:
            rates = fetch_rates(self._base, self._symbols)
            updated_at = SqliteExchangeRateRepository.utc_now_iso()
            for symbol, api_rate in rates.items():
                if symbol == self._base:
                    continue
                self._exchange_rate_repo.upsert(
                    ExchangeRateUpsertDto(
                        from_currency=symbol,
                        to_currency=self._base,
                        rate=_api_rate_to_normalizer_rate(api_rate),
                        updated_at=updated_at,
                    )
                )
            if not use_mock_rates():
                record_successful_fetch()
            self.signals.finished.emit(rates)
        except Exception as exc:
            self.signals.error.emit(str(exc))
