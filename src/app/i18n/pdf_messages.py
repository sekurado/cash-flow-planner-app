from __future__ import annotations

from PySide6.QtCore import QCoreApplication

_CONTEXT = "PdfExport"


def _translate(source: str, *args: str) -> str:
    translated = QCoreApplication.translate(_CONTEXT, source)
    if not args:
        return translated
    result = translated
    for index, arg in enumerate(args, start=1):
        result = result.replace(f"%{index}", arg)
    return result


def pdf_report_title(plan_name: str) -> str:
    return _translate("%1 — Projection report", plan_name)


def pdf_forecast_horizon_label() -> str:
    return _translate("Forecast horizon:")


def pdf_exported_at_label() -> str:
    return _translate("Exported at:")


def pdf_app_version_label() -> str:
    return _translate("App version:")


def pdf_methodology_version_label() -> str:
    return _translate("Methodology version:")


def pdf_display_currency_label() -> str:
    return _translate("Display currency:")


def pdf_section_monthly_cash_bridge() -> str:
    return _translate("Monthly cash bridge")


def pdf_section_balance_chart() -> str:
    return _translate("Balance chart")


def pdf_section_fx_footnotes() -> str:
    return _translate("FX footnotes")


def pdf_section_scenario_comparison() -> str:
    return _translate("Scenario comparison")


def pdf_active_overrides_label() -> str:
    return _translate("Active overrides:")


def pdf_fx_normalization_note(currency: str) -> str:
    return _translate(
        "All amounts in this report are normalized to %1 using the rates above.",
        currency,
    )


def pdf_cash_bridge_headers() -> tuple[str, ...]:
    return (
        _translate("Year"),
        _translate("Month"),
        _translate("Opening"),
        _translate("Inflows"),
        _translate("Outflows"),
        _translate("Net"),
        _translate("Closing"),
    )


def pdf_scenario_headers() -> tuple[str, ...]:
    return (
        _translate("Metric"),
        _translate("Baseline"),
        _translate("Scenario"),
        _translate("Delta"),
    )


def pdf_fx_footnote_headers() -> tuple[str, ...]:
    return (
        _translate("From"),
        _translate("To"),
        _translate("Rate"),
        _translate("Updated at"),
    )


def pdf_metric_final_balance() -> str:
    return _translate("Final balance")


def pdf_metric_first_cash_shortfall_date() -> str:
    return _translate("First cash shortfall date")


def pdf_metric_total_inflows() -> str:
    return _translate("Total inflows")


def pdf_metric_total_outflows() -> str:
    return _translate("Total outflows")


def pdf_deficit_date_none() -> str:
    return _translate("None")


def pdf_deficit_date_only_in_scenario() -> str:
    return _translate("Only in scenario")


def pdf_deficit_date_only_in_baseline() -> str:
    return _translate("Only in baseline")


def pdf_deficit_date_delta_days(days: int) -> str:
    if days > 0:
        return _translate("+%1 days", str(days))
    return _translate("%1 days", str(days))


def pdf_money_delta_zero() -> str:
    return _translate("—")


def _register_i18n_catalog() -> None:
    """Literal translate() calls for pyside6-lupdate extraction only."""
    QCoreApplication.translate("PdfExport", "%1 — Projection report")
    QCoreApplication.translate("PdfExport", "Forecast horizon:")
    QCoreApplication.translate("PdfExport", "Exported at:")
    QCoreApplication.translate("PdfExport", "App version:")
    QCoreApplication.translate("PdfExport", "Methodology version:")
    QCoreApplication.translate("PdfExport", "Display currency:")
    QCoreApplication.translate("PdfExport", "Monthly cash bridge")
    QCoreApplication.translate("PdfExport", "Balance chart")
    QCoreApplication.translate("PdfExport", "FX footnotes")
    QCoreApplication.translate("PdfExport", "Scenario comparison")
    QCoreApplication.translate("PdfExport", "Active overrides:")
    QCoreApplication.translate(
        "PdfExport",
        "All amounts in this report are normalized to %1 using the rates above.",
    )
    QCoreApplication.translate("PdfExport", "Year")
    QCoreApplication.translate("PdfExport", "Month")
    QCoreApplication.translate("PdfExport", "Opening")
    QCoreApplication.translate("PdfExport", "Inflows")
    QCoreApplication.translate("PdfExport", "Outflows")
    QCoreApplication.translate("PdfExport", "Net")
    QCoreApplication.translate("PdfExport", "Closing")
    QCoreApplication.translate("PdfExport", "Metric")
    QCoreApplication.translate("PdfExport", "Baseline")
    QCoreApplication.translate("PdfExport", "Scenario")
    QCoreApplication.translate("PdfExport", "Delta")
    QCoreApplication.translate("PdfExport", "From")
    QCoreApplication.translate("PdfExport", "To")
    QCoreApplication.translate("PdfExport", "Rate")
    QCoreApplication.translate("PdfExport", "Updated at")
    QCoreApplication.translate("PdfExport", "Final balance")
    QCoreApplication.translate("PdfExport", "First cash shortfall date")
    QCoreApplication.translate("PdfExport", "Total inflows")
    QCoreApplication.translate("PdfExport", "Total outflows")
    QCoreApplication.translate("PdfExport", "None")
    QCoreApplication.translate("PdfExport", "Only in scenario")
    QCoreApplication.translate("PdfExport", "Only in baseline")
    QCoreApplication.translate("PdfExport", "+%1 days")
    QCoreApplication.translate("PdfExport", "%1 days")
    QCoreApplication.translate("PdfExport", "—")
