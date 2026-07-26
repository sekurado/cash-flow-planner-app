from __future__ import annotations

import re
from re import Pattern

from pydantic import ValidationError
from PySide6.QtCore import QCoreApplication, QSettings

from src.domain.date_pattern import PatternType, parse_pattern
from src.domain.exceptions import DatePatternParseError

_MONTH_CONTEXT = "MonthlyTableView"
_PATTERN_CONTEXT = "EntriesViewModel"
_ERROR_CONTEXT = "AppErrors"
_TEMPLATE_CONTEXT = "ForecastTemplates"

_MONTH_SOURCES = (
    "",
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)

_STATIC_ERRORS: dict[str, str] = {
    "Invalid data. Please check your input.": "Invalid data. Please check your input.",
    "Live exchange-rate fetching is not enabled.": "Live exchange-rate fetching is not enabled.",
    "Base currency is required to fetch live exchange rates.": (
        "Base currency is required to fetch live exchange rates."
    ),
    "No simulation result to export.": "No projection result to export.",
    "Name is required": "Name is required",
    "Currency is required": "Currency is required",
    "Exchange rate API returned invalid JSON": "Exchange rate API returned invalid JSON",
    "Exchange rate API response is missing conversion rates": (
        "Exchange rate API response is missing conversion rates"
    ),
    "Exchange rate API returned a zero rate": "Exchange rate API returned a zero rate",
    "Simulation params must include a numeric initial_balance": (
        "Simulation params must include a numeric initial_balance"
    ),
    "Simulation params must include a non-empty base_currency": (
        "Simulation params must include a non-empty base_currency"
    ),
    "Simulation params must include ISO start_date and end_date": (
        "Simulation params must include ISO start_date and end_date"
    ),
    "Exchange rates must target USD, got GBP": ("Exchange rates must target USD, got GBP"),
    "Exchange rates cannot use USD as the source currency": (
        "Exchange rates cannot use USD as the source currency"
    ),
    "User manual is not available.": "User manual is not available.",
    "Could not open the user manual.": "Could not open the user manual.",
}

_ERROR_PATTERNS: list[tuple[Pattern[str], str]] = [
    (re.compile(r"^Plan not found: (.+)$"), "Forecast not found: %1"),
    (
        re.compile(r"^Plan name already exists: (.+)$"),
        'A forecast named "%1" already exists',
    ),
    (re.compile(r"^Entry not found: (.+)$"), "Cash flow not found: %1"),
    (re.compile(r"^Invalid date pattern: (.+)$"), "Invalid date pattern: %1"),
    (re.compile(r"^Unsupported file type: (.+)$"), "Unsupported file type: %1"),
    (
        re.compile(r"^No exchange rate found for (.+) → (.+)$"),
        "No exchange rate found for %1 → %2",
    ),
    (
        re.compile(r"^Simulation range of (\d+) days exceeds the (\d+)-day \(10-year\) limit$"),
        "Simulation range of %1 days exceeds the %2-day (10-year) limit",
    ),
    (
        re.compile(r"^Exchange rate API returned HTTP (\d+)$"),
        "Exchange rate API returned HTTP %1",
    ),
    (
        re.compile(r"^Mock exchange rates are not defined for base currency (.+)$"),
        "Mock exchange rates are not defined for base currency %1",
    ),
    (
        re.compile(r"^Mock exchange rates are missing symbols: (.+)$"),
        "Mock exchange rates are missing symbols: %1",
    ),
    (re.compile(r"^(.+) must be a mapping$"), "%1 must be a mapping"),
    (
        re.compile(r"^Daily live rate fetch limit reached \(10 per day\)\. Try again tomorrow\.$"),
        "Daily live rate fetch limit reached (10 per day). Try again tomorrow.",
    ),
    (
        re.compile(r"^Please wait (\d+) second\(s\) before fetching live rates again\.$"),
        "Please wait %1 second(s) before fetching live rates again.",
    ),
    (
        re.compile(r"^Please wait (\d+) minute\(s\) before fetching live rates again\.$"),
        "Please wait %1 minute(s) before fetching live rates again.",
    ),
]


def _apply_placeholders(template: str, args: tuple[str, ...]) -> str:
    result = template
    for index, arg in enumerate(args, start=1):
        result = result.replace(f"%{index}", arg)
    return result


def _translate(context: str, source: str, *args: str) -> str:
    translated = QCoreApplication.translate(context, source)
    if not args:
        return translated
    return _apply_placeholders(translated, args)


def _uses_english_ordinals() -> bool:
    lang = QSettings().value("language", "en")
    return not isinstance(lang, str) or lang == "en"


def localized_month_abbrev(month: int) -> str:
    if not 1 <= month <= 12:
        return str(month)
    return QCoreApplication.translate(_MONTH_CONTEXT, _MONTH_SOURCES[month])


def localized_day_of_month(day: int) -> str:
    if not _uses_english_ordinals():
        return str(day)
    if 11 <= (day % 100) <= 13:
        return f"{day}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{day}{suffix}"


def describe_pattern_text(raw: str) -> str:
    try:
        pattern = parse_pattern(raw)
    except DatePatternParseError:
        return ""

    match pattern.type:
        case PatternType.DAILY:
            return QCoreApplication.translate(_PATTERN_CONTEXT, "Every day")
        case PatternType.MONTHLY:
            if pattern.day is None:
                return ""
            return _translate(
                _PATTERN_CONTEXT,
                "Monthly on the %1",
                localized_day_of_month(pattern.day),
            )
        case PatternType.YEARLY:
            if pattern.day is None or pattern.month is None:
                return ""
            return _translate(
                _PATTERN_CONTEXT,
                "Yearly on %1 %2",
                str(pattern.day),
                localized_month_abbrev(pattern.month),
            )
        case PatternType.ONE_TIME:
            if pattern.day is None or pattern.month is None or pattern.year is None:
                return ""
            return _translate(
                _PATTERN_CONTEXT,
                "Once on %1 %2 %3",
                str(pattern.day),
                localized_month_abbrev(pattern.month),
                str(pattern.year),
            )


def translate_user_message(message: str) -> str:
    source = message.strip()
    if not source:
        return ""

    static_source = _STATIC_ERRORS.get(source)
    if static_source is not None:
        return QCoreApplication.translate(_ERROR_CONTEXT, static_source)

    for pattern, template in _ERROR_PATTERNS:
        match = pattern.fullmatch(source)
        if match is None:
            continue
        return _translate(_ERROR_CONTEXT, template, *match.groups())

    return source


def translate_template_text(source: str) -> str:
    return QCoreApplication.translate(_TEMPLATE_CONTEXT, source)


def validation_error_message() -> str:
    return translate_user_message("Invalid data. Please check your input.")


def format_view_model_error(exc: BaseException) -> str:
    if isinstance(exc, ValidationError):
        return validation_error_message()
    return translate_user_message(str(exc))


def _register_i18n_catalog() -> None:
    """Literal translate() calls for pyside6-lupdate extraction only."""
    QCoreApplication.translate("AppErrors", "Invalid data. Please check your input.")
    QCoreApplication.translate("AppErrors", "Live exchange-rate fetching is not enabled.")
    QCoreApplication.translate(
        "AppErrors", "Base currency is required to fetch live exchange rates."
    )
    QCoreApplication.translate("AppErrors", "No projection result to export.")
    QCoreApplication.translate("AppErrors", "Name is required")
    QCoreApplication.translate("AppErrors", "Currency is required")
    QCoreApplication.translate("AppErrors", "Exchange rate API returned invalid JSON")
    QCoreApplication.translate(
        "AppErrors", "Exchange rate API response is missing conversion rates"
    )
    QCoreApplication.translate("AppErrors", "Exchange rate API returned a zero rate")
    QCoreApplication.translate(
        "AppErrors", "Simulation params must include a numeric initial_balance"
    )
    QCoreApplication.translate(
        "AppErrors", "Simulation params must include a non-empty base_currency"
    )
    QCoreApplication.translate(
        "AppErrors", "Simulation params must include ISO start_date and end_date"
    )
    QCoreApplication.translate("AppErrors", "Exchange rates must target USD, got GBP")
    QCoreApplication.translate("AppErrors", "Exchange rates cannot use USD as the source currency")
    QCoreApplication.translate("AppErrors", "Forecast not found: %1")
    QCoreApplication.translate("AppErrors", 'A forecast named "%1" already exists')
    QCoreApplication.translate("AppErrors", "Cash flow not found: %1")
    QCoreApplication.translate("AppErrors", "Invalid date pattern: %1")
    QCoreApplication.translate("AppErrors", "Unsupported file type: %1")
    QCoreApplication.translate("AppErrors", "No exchange rate found for %1 → %2")
    QCoreApplication.translate(
        "AppErrors", "Simulation range of %1 days exceeds the %2-day (10-year) limit"
    )
    QCoreApplication.translate("AppErrors", "Exchange rate API returned HTTP %1")
    QCoreApplication.translate(
        "AppErrors", "Mock exchange rates are not defined for base currency %1"
    )
    QCoreApplication.translate("AppErrors", "Mock exchange rates are missing symbols: %1")
    QCoreApplication.translate("AppErrors", "%1 must be a mapping")
    QCoreApplication.translate(
        "AppErrors", "Daily live rate fetch limit reached (10 per day). Try again tomorrow."
    )
    QCoreApplication.translate(
        "AppErrors", "Please wait %1 second(s) before fetching live rates again."
    )
    QCoreApplication.translate(
        "AppErrors", "Please wait %1 minute(s) before fetching live rates again."
    )
    QCoreApplication.translate("AppErrors", "User manual is not available.")
    QCoreApplication.translate("AppErrors", "Could not open the user manual.")
    QCoreApplication.translate("EntriesViewModel", "Every day")
    QCoreApplication.translate("EntriesViewModel", "Monthly on the %1")
    QCoreApplication.translate("EntriesViewModel", "Yearly on %1 %2")
    QCoreApplication.translate("EntriesViewModel", "Once on %1 %2 %3")
    QCoreApplication.translate("ForecastTemplates", "SaaS startup")
    QCoreApplication.translate(
        "ForecastTemplates",
        "Monthly recurring revenue, cloud costs, and payroll for an early-stage SaaS company.",
    )
    QCoreApplication.translate("ForecastTemplates", "Consulting firm")
    QCoreApplication.translate(
        "ForecastTemplates",
        "Client retainers, contractor costs, and operating expenses "
        "for a small professional services firm.",
    )
    QCoreApplication.translate("ForecastTemplates", "Retail shop")
    QCoreApplication.translate(
        "ForecastTemplates",
        "Point-of-sale revenue, rent, inventory COGS, and seasonal patterns "
        "for a brick-and-mortar retail store.",
    )
    from src.app.i18n.suggestion_copy import _register_i18n_catalog as _register_suggestion_catalog

    _register_suggestion_catalog()
