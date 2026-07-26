from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QCoreApplication

from src.export.metadata import METHODOLOGY_VERSION

_CONTEXT = "Methodology"

_PATTERN_LITERALS = ("...", "10..", "15.03.", "15.03.2026")


@dataclass(frozen=True)
class MethodologySection:
    group_title: str
    heading: str
    body: str


def _translate(source: str) -> str:
    return QCoreApplication.translate(_CONTEXT, source)


def methodology_heading() -> str:
    return _translate("Methodology")


def methodology_version_line() -> str:
    return _translate("Methodology version: %1").replace("%1", METHODOLOGY_VERSION)


def methodology_intro() -> str:
    return _translate(
        "This page explains how Cash Flow Planner computes projections, "
        "detects cash shortfalls, and handles currencies and scenarios."
    )


def methodology_pattern_examples_heading() -> str:
    return _translate("Pattern examples")


def methodology_pattern_descriptions() -> tuple[str, ...]:
    return (
        _translate("Every day (daily)"),
        _translate("Monthly on the 10th"),
        _translate("Yearly on 15 March"),
        _translate("One-time on 15 March 2026"),
    )


def methodology_pattern_examples() -> tuple[tuple[str, str], ...]:
    return tuple(zip(_PATTERN_LITERALS, methodology_pattern_descriptions(), strict=True))


def is_date_patterns_group(group_title: str) -> bool:
    return group_title == _translate("Date patterns")


def methodology_sections() -> tuple[MethodologySection, ...]:
    return (
        MethodologySection(
            group_title=_translate("Cash shortfall detection"),
            heading=_translate("Daily running balance"),
            body=_translate(
                "Each forecast run starts from your opening cash balance. "
                "For every calendar day in the projection range, the app sums "
                "income and expenses scheduled on that day, then computes:\n\n"
                "closing balance = previous closing balance + income − expenses\n\n"
                "The previous day’s closing balance becomes the next day’s "
                "starting point, producing a day-by-day running balance."
            ),
        ),
        MethodologySection(
            group_title=_translate("Cash shortfall detection"),
            heading=_translate("First cash shortfall"),
            body=_translate(
                "A cash shortfall is reported on the first day whose closing balance "
                "falls below zero. When that happens, the app records the date "
                "and highlights the expense cash flow that contributed to the "
                "shortfall on that day (or the first scheduled event if no "
                "expense occurred). Later shortfalls are not reported separately—"
                "only the earliest one is shown."
            ),
        ),
        MethodologySection(
            group_title=_translate("Date patterns"),
            heading=_translate("How cash flows are scheduled"),
            body=_translate(
                "Each cash flow uses a compact date pattern. The pattern is expanded "
                "into individual dated events across the forecast range before "
                "the running balance is calculated. Patterns are validated as "
                "you type when editing a cash flow."
            ),
        ),
        MethodologySection(
            group_title=_translate("Multi-currency normalization"),
            heading=_translate("Base currency conversion"),
            body=_translate(
                "Cash flows may be entered in different currencies. Before amounts are "
                "summed, each event is converted to the forecast’s base currency "
                "using stored exchange rates. Direct rates (e.g. EUR → USD) are "
                "used when available; otherwise an inverse rate is applied."
            ),
        ),
        MethodologySection(
            group_title=_translate("Multi-currency normalization"),
            heading=_translate("Exchange rate sources"),
            body=_translate(
                "Rates are managed globally in Settings. You can enter rates manually "
                "or enable live fetching to download current rates from an external "
                "provider when network access is available. A forecast run fails "
                "with a clear error if a required conversion rate is missing."
            ),
        ),
        MethodologySection(
            group_title=_translate("Scenario planning"),
            heading=_translate("Temporary overrides"),
            body=_translate(
                "Scenario mode lets you adjust cash-flow amounts or deactivate line "
                "items to explore alternatives. Overrides are applied only for "
                "the current forecast run—they are not saved to your forecast "
                "and do not change stored cash flows. Clear overrides or leave "
                "the scenario panel to return to the saved baseline."
            ),
        ),
    )


def _register_i18n_catalog() -> None:
    """Literal translate() calls for pyside6-lupdate extraction only."""
    QCoreApplication.translate("Methodology", "Methodology")
    QCoreApplication.translate("Methodology", "Methodology version: %1")
    QCoreApplication.translate(
        "Methodology",
        "This page explains how Cash Flow Planner computes projections, "
        "detects cash shortfalls, and handles currencies and scenarios.",
    )
    QCoreApplication.translate("Methodology", "Cash shortfall detection")
    QCoreApplication.translate("Methodology", "Daily running balance")
    QCoreApplication.translate(
        "Methodology",
        "Each forecast run starts from your opening cash balance. "
        "For every calendar day in the projection range, the app sums "
        "income and expenses scheduled on that day, then computes:\n\n"
        "closing balance = previous closing balance + income − expenses\n\n"
        "The previous day’s closing balance becomes the next day’s "
        "starting point, producing a day-by-day running balance.",
    )
    QCoreApplication.translate("Methodology", "First cash shortfall")
    QCoreApplication.translate(
        "Methodology",
        "A cash shortfall is reported on the first day whose closing balance "
        "falls below zero. When that happens, the app records the date "
        "and highlights the expense cash flow that contributed to the "
        "shortfall on that day (or the first scheduled event if no "
        "expense occurred). Later shortfalls are not reported separately—"
        "only the earliest one is shown.",
    )
    QCoreApplication.translate("Methodology", "Date patterns")
    QCoreApplication.translate("Methodology", "How cash flows are scheduled")
    QCoreApplication.translate(
        "Methodology",
        "Each cash flow uses a compact date pattern. The pattern is expanded "
        "into individual dated events across the forecast range before "
        "the running balance is calculated. Patterns are validated as "
        "you type when editing a cash flow.",
    )
    QCoreApplication.translate("Methodology", "Pattern examples")
    QCoreApplication.translate("Methodology", "Every day (daily)")
    QCoreApplication.translate("Methodology", "Monthly on the 10th")
    QCoreApplication.translate("Methodology", "Yearly on 15 March")
    QCoreApplication.translate("Methodology", "One-time on 15 March 2026")
    QCoreApplication.translate("Methodology", "Multi-currency normalization")
    QCoreApplication.translate("Methodology", "Base currency conversion")
    QCoreApplication.translate(
        "Methodology",
        "Cash flows may be entered in different currencies. Before amounts are "
        "summed, each event is converted to the forecast’s base currency "
        "using stored exchange rates. Direct rates (e.g. EUR → USD) are "
        "used when available; otherwise an inverse rate is applied.",
    )
    QCoreApplication.translate("Methodology", "Exchange rate sources")
    QCoreApplication.translate(
        "Methodology",
        "Rates are managed globally in Settings. You can enter rates manually "
        "or enable live fetching to download current rates from an external "
        "provider when network access is available. A forecast run fails "
        "with a clear error if a required conversion rate is missing.",
    )
    QCoreApplication.translate("Methodology", "Scenario planning")
    QCoreApplication.translate("Methodology", "Temporary overrides")
    QCoreApplication.translate(
        "Methodology",
        "Scenario mode lets you adjust cash-flow amounts or deactivate line "
        "items to explore alternatives. Overrides are applied only for "
        "the current forecast run—they are not saved to your forecast "
        "and do not change stored cash flows. Clear overrides or leave "
        "the scenario panel to return to the saved baseline.",
    )
