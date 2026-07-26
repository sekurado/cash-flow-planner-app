from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime
from pathlib import Path

from reportlab.lib import colors  # type: ignore[import-untyped]
from reportlab.lib.pagesizes import letter  # type: ignore[import-untyped]
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # type: ignore[import-untyped]
from reportlab.lib.units import inch  # type: ignore[import-untyped]
from reportlab.platypus import (  # type: ignore[import-untyped]
    Flowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.app.i18n.methodology_content import (
    is_date_patterns_group,
    methodology_heading,
    methodology_intro,
    methodology_pattern_examples,
    methodology_pattern_examples_heading,
    methodology_sections,
    methodology_version_line,
)
from src.app.i18n.pdf_messages import (
    pdf_active_overrides_label,
    pdf_app_version_label,
    pdf_cash_bridge_headers,
    pdf_deficit_date_delta_days,
    pdf_deficit_date_none,
    pdf_deficit_date_only_in_baseline,
    pdf_deficit_date_only_in_scenario,
    pdf_display_currency_label,
    pdf_exported_at_label,
    pdf_forecast_horizon_label,
    pdf_fx_footnote_headers,
    pdf_fx_normalization_note,
    pdf_methodology_version_label,
    pdf_metric_final_balance,
    pdf_metric_first_cash_shortfall_date,
    pdf_metric_total_inflows,
    pdf_metric_total_outflows,
    pdf_money_delta_zero,
    pdf_report_title,
    pdf_scenario_headers,
    pdf_section_balance_chart,
    pdf_section_fx_footnotes,
    pdf_section_monthly_cash_bridge,
    pdf_section_scenario_comparison,
)
from src.domain.currency_normalizer import convert_amount
from src.domain.entities import ExchangeRate, SimulationResult
from src.domain.exceptions import ExportError
from src.export._atomic import atomic_write
from src.export._display_currency import convert_result_for_display
from src.export.balance_chart_pdf import build_balance_chart_drawing
from src.export.cash_bridge import build_cash_bridge
from src.export.metadata import metadata_from_export_context
from src.export.models import CashBridgeMonth, EntriesSummary, ExportContext
from src.export.pdf_colors import (
    DEFICIT_AMBER_BG,
    EXPENSE_RED,
    INCOME_GREEN,
    NEUTRAL_TEXT,
    TABLE_HEADER_BG,
    delta_text_color,
    money_text_color,
)
from src.export.pdf_fonts import pdf_font_name

_CHART_HEIGHT = 2.25 * inch

_FONT_NAME = pdf_font_name()
_SECTION_HEADING = "Heading2"


def _round_money(value: float) -> float:
    return round(value, 2)


def _format_money(value: float, currency: str) -> str:
    return f"{_round_money(value):.2f} {currency}"


def _cash_bridge_row_cells(row: CashBridgeMonth, currency: str) -> list[str]:
    return [
        str(row.year),
        str(row.month),
        _format_money(row.opening_balance, currency),
        _format_money(row.total_inflows, currency),
        _format_money(row.total_outflows, currency),
        _format_money(row.net_flow, currency),
        _format_money(row.closing_balance, currency),
    ]


def cash_bridge_table_data(
    bridge: tuple[CashBridgeMonth, ...],
    currency: str,
) -> list[list[str]]:
    """Return cash-bridge table rows including the header row."""
    table_data = [list(pdf_cash_bridge_headers())]
    table_data.extend(_cash_bridge_row_cells(row, currency) for row in bridge)
    return table_data


def _format_deficit_date(value: date | None) -> str:
    return value.isoformat() if value is not None else pdf_deficit_date_none()


def _deficit_date_delta(baseline: date | None, scenario: date | None) -> str:
    if baseline == scenario:
        return pdf_money_delta_zero()
    if baseline is None and scenario is not None:
        return pdf_deficit_date_only_in_scenario()
    if baseline is not None and scenario is None:
        return pdf_deficit_date_only_in_baseline()
    assert baseline is not None and scenario is not None
    return pdf_deficit_date_delta_days((scenario - baseline).days)


def _money_delta(scenario: float, baseline: float, currency: str) -> str:
    delta = _round_money(scenario - baseline)
    if delta == 0:
        return pdf_money_delta_zero()
    signed = f"+{delta:.2f}" if delta > 0 else f"{delta:.2f}"
    return f"{signed} {currency}"


def fx_footnotes_table_data(exchange_rates: tuple[ExchangeRate, ...]) -> list[list[str]]:
    """Return FX footnote rows including the header row."""
    table_data = [list(pdf_fx_footnote_headers())]
    table_data.extend(
        [
            rate.from_currency,
            rate.to_currency,
            str(rate.rate),
            rate.updated_at,
        ]
        for rate in exchange_rates
    )
    return table_data


def _base_table_style() -> TableStyle:
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, -1), _FONT_NAME),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]
    )


def _cash_bridge_table_style(
    bridge: tuple[CashBridgeMonth, ...],
    export_result: SimulationResult,
) -> TableStyle:
    table_style = _base_table_style()
    snapshots_by_month = {
        (snapshot.year, snapshot.month): snapshot for snapshot in export_result.monthly_snapshots
    }
    for row_index, row in enumerate(bridge, start=1):
        snapshot = snapshots_by_month.get((row.year, row.month))
        if snapshot is not None and snapshot.deficit:
            table_style.add(
                "BACKGROUND",
                (0, row_index),
                (-1, row_index),
                DEFICIT_AMBER_BG,
            )
        table_style.add("TEXTCOLOR", (2, row_index), (2, row_index), NEUTRAL_TEXT)
        table_style.add("TEXTCOLOR", (3, row_index), (3, row_index), INCOME_GREEN)
        table_style.add("TEXTCOLOR", (4, row_index), (4, row_index), EXPENSE_RED)
        table_style.add(
            "TEXTCOLOR",
            (5, row_index),
            (5, row_index),
            money_text_color(row.net_flow),
        )
        table_style.add(
            "TEXTCOLOR",
            (6, row_index),
            (6, row_index),
            money_text_color(row.closing_balance),
        )
    return table_style


def _scenario_comparison_table_style(
    baseline: SimulationResult,
    scenario: SimulationResult,
) -> TableStyle:
    table_style = _base_table_style()
    money_deltas: list[tuple[float, bool] | None] = [
        (scenario.final_balance - baseline.final_balance, True),
        None,
        (scenario.total_income - baseline.total_income, True),
        (scenario.total_expense - baseline.total_expense, False),
    ]
    for row_index, delta_spec in enumerate(money_deltas, start=1):
        if delta_spec is None:
            continue
        delta_value, higher_is_better = delta_spec
        table_style.add(
            "TEXTCOLOR",
            (3, row_index),
            (3, row_index),
            delta_text_color(_round_money(delta_value), higher_is_better=higher_is_better),
        )
    return table_style


def _cover_metadata_lines(context: ExportContext) -> str:
    meta = metadata_from_export_context(context)
    params = context.result.params
    date_range = f"{params.start_date.isoformat()} — {params.end_date.isoformat()}"
    return (
        f"{pdf_forecast_horizon_label()} {date_range}<br/>"
        f"{pdf_exported_at_label()} {meta.exported_at}<br/>"
        f"{pdf_app_version_label()} {meta.app_version}<br/>"
        f"{pdf_methodology_version_label()} {meta.methodology_version}<br/>"
        f"{pdf_display_currency_label()} {meta.display_currency}"
    )


def scenario_comparison_table_data(
    baseline: SimulationResult,
    scenario: SimulationResult,
    currency: str,
) -> list[list[str]]:
    """Return scenario comparison rows including the header row."""
    return [
        list(pdf_scenario_headers()),
        [
            pdf_metric_final_balance(),
            _format_money(baseline.final_balance, currency),
            _format_money(scenario.final_balance, currency),
            _money_delta(scenario.final_balance, baseline.final_balance, currency),
        ],
        [
            pdf_metric_first_cash_shortfall_date(),
            _format_deficit_date(baseline.first_deficit_date),
            _format_deficit_date(scenario.first_deficit_date),
            _deficit_date_delta(baseline.first_deficit_date, scenario.first_deficit_date),
        ],
        [
            pdf_metric_total_inflows(),
            _format_money(baseline.total_income, currency),
            _format_money(scenario.total_income, currency),
            _money_delta(scenario.total_income, baseline.total_income, currency),
        ],
        [
            pdf_metric_total_outflows(),
            _format_money(baseline.total_expense, currency),
            _format_money(scenario.total_expense, currency),
            _money_delta(scenario.total_expense, baseline.total_expense, currency),
        ],
    ]


def _convert_for_export(context: ExportContext) -> SimulationResult:
    result = context.result
    if context.display_currency != result.params.base_currency and context.exchange_rates:
        return convert_result_for_display(
            result,
            context.display_currency,
            list(context.exchange_rates),
        )
    return result


def _build_cash_bridge_for_export(
    context: ExportContext,
    export_result: SimulationResult,
) -> tuple[CashBridgeMonth, ...]:
    bridge_source = export_result
    if context.display_currency != context.result.params.base_currency:
        converted_opening = convert_amount(
            context.result.params.initial_balance,
            context.result.params.base_currency,
            context.display_currency,
            list(context.exchange_rates),
        )
        bridge_source = replace(
            export_result,
            params=replace(export_result.params, initial_balance=converted_opening),
        )
    return build_cash_bridge(bridge_source)


def _daily_balances_for_chart(
    context: ExportContext,
    export_result: SimulationResult,
) -> list[tuple[date, float]]:
    source_currency = context.result.params.base_currency
    display_currency = context.display_currency
    exchange_rates = list(context.exchange_rates)
    chart_points: list[tuple[date, float]] = []
    for daily in export_result.daily_balances:
        balance = daily.closing_balance
        if display_currency != source_currency and exchange_rates:
            balance = convert_amount(
                balance,
                source_currency,
                display_currency,
                exchange_rates,
            )
        chart_points.append((daily.date, balance))
    return chart_points


def _balance_chart_story(
    context: ExportContext,
    export_result: SimulationResult,
    heading_style: ParagraphStyle,
    *,
    chart_width: float,
) -> list[Flowable]:
    chart_points = _daily_balances_for_chart(context, export_result)
    if not chart_points:
        return []
    return [
        Paragraph(pdf_section_balance_chart(), heading_style),
        Spacer(1, 0.1 * inch),
        build_balance_chart_drawing(
            chart_points,
            currency=context.display_currency,
            width=chart_width,
            height=_CHART_HEIGHT,
        ),
        Spacer(1, 0.25 * inch),
    ]


def _build_story(
    context: ExportContext,
    export_result: SimulationResult,
    bridge: tuple[CashBridgeMonth, ...],
    *,
    baseline_export_result: SimulationResult | None = None,
) -> list[Flowable]:
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ExportTitle",
        parent=styles["Title"],
        fontName=_FONT_NAME,
    )
    body_style = ParagraphStyle(
        "ExportBody",
        parent=styles["Normal"],
        fontName=_FONT_NAME,
    )
    heading_style = ParagraphStyle(
        "ExportHeading",
        parent=styles[_SECTION_HEADING],
        fontName=_FONT_NAME,
    )

    story: list[Flowable] = [
        Paragraph(pdf_report_title(context.plan_name), title_style),
        Paragraph(_cover_metadata_lines(context), body_style),
        Spacer(1, 0.25 * inch),
    ]
    chart_width = letter[0] - 1.5 * inch
    story.extend(
        _balance_chart_story(
            context,
            export_result,
            heading_style,
            chart_width=chart_width,
        )
    )
    story.extend(
        [
            Paragraph(pdf_section_monthly_cash_bridge(), heading_style),
            Spacer(1, 0.1 * inch),
        ]
    )

    table_data = cash_bridge_table_data(bridge, context.display_currency)
    table = Table(table_data, repeatRows=1)
    table.setStyle(_cash_bridge_table_style(bridge, export_result))
    story.append(table)

    if baseline_export_result is not None:
        story.extend(
            _scenario_comparison_story(
                context,
                baseline_export_result,
                export_result,
                heading_style,
                body_style,
            )
        )
    story.extend(_fx_footnotes_story(context, heading_style, body_style))
    story.extend(_methodology_story(heading_style, body_style))
    return story


def _fx_footnotes_story(
    context: ExportContext,
    heading_style: ParagraphStyle,
    body_style: ParagraphStyle,
) -> list[Flowable]:
    if not context.exchange_rates:
        return []
    story: list[Flowable] = [
        Spacer(1, 0.25 * inch),
        Paragraph(pdf_section_fx_footnotes(), heading_style),
        Spacer(1, 0.1 * inch),
    ]
    table_data = fx_footnotes_table_data(context.exchange_rates)
    table = Table(table_data, repeatRows=1)
    table.setStyle(_base_table_style())
    story.append(table)
    story.extend(
        [
            Spacer(1, 0.1 * inch),
            Paragraph(pdf_fx_normalization_note(context.display_currency), body_style),
        ]
    )
    return story


def _paragraph_body_html(text: str) -> str:
    return text.replace("\n\n", "<br/><br/>")


def _methodology_story(
    heading_style: ParagraphStyle,
    body_style: ParagraphStyle,
) -> list[Flowable]:
    story: list[Flowable] = [
        Spacer(1, 0.25 * inch),
        Paragraph(methodology_heading(), heading_style),
        Spacer(1, 0.1 * inch),
        Paragraph(methodology_version_line(), body_style),
        Spacer(1, 0.1 * inch),
        Paragraph(_paragraph_body_html(methodology_intro()), body_style),
    ]

    current_group = ""
    for section in methodology_sections():
        if section.group_title != current_group:
            current_group = section.group_title
            story.extend(
                [
                    Spacer(1, 0.15 * inch),
                    Paragraph(f"<b>{current_group}</b>", body_style),
                ]
            )
        body_html = _paragraph_body_html(section.body)
        story.append(
            Paragraph(
                f"<b>{section.heading}</b><br/>{body_html}",
                body_style,
            )
        )
        if is_date_patterns_group(section.group_title):
            example_lines = "<br/>".join(
                f'• <font face="Courier">{pattern}</font> — {description}'
                for pattern, description in methodology_pattern_examples()
            )
            story.extend(
                [
                    Spacer(1, 0.05 * inch),
                    Paragraph(
                        (f"<b>{methodology_pattern_examples_heading()}</b><br/>{example_lines}"),
                        body_style,
                    ),
                ]
            )

    story.append(Spacer(1, 0.25 * inch))
    return story


def _scenario_comparison_story(
    context: ExportContext,
    baseline_result: SimulationResult,
    scenario_result: SimulationResult,
    heading_style: ParagraphStyle,
    body_style: ParagraphStyle,
) -> list[Flowable]:
    story: list[Flowable] = [
        Spacer(1, 0.25 * inch),
        Paragraph(pdf_section_scenario_comparison(), heading_style),
        Spacer(1, 0.1 * inch),
    ]
    table_data = scenario_comparison_table_data(
        baseline_result,
        scenario_result,
        context.display_currency,
    )
    table = Table(table_data, repeatRows=1)
    table.setStyle(_scenario_comparison_table_style(baseline_result, scenario_result))
    story.append(table)
    if context.override_footnotes:
        footnote_lines = "<br/>".join(f"• {line}" for line in context.override_footnotes)
        story.extend(
            [
                Spacer(1, 0.1 * inch),
                Paragraph(f"{pdf_active_overrides_label()}<br/>{footnote_lines}", body_style),
            ]
        )
    return story


class PdfExporter:
    @staticmethod
    def export(context: ExportContext, path: Path) -> None:
        export_result = _convert_for_export(context)
        bridge = _build_cash_bridge_for_export(context, export_result)
        baseline_export_result: SimulationResult | None = None
        if context.baseline_result is not None:
            baseline_context = context.model_copy(update={"result": context.baseline_result})
            baseline_export_result = _convert_for_export(baseline_context)

        def _write(target: Path) -> None:
            doc = SimpleDocTemplate(
                str(target),
                pagesize=letter,
                leftMargin=0.75 * inch,
                rightMargin=0.75 * inch,
                topMargin=0.75 * inch,
                bottomMargin=0.75 * inch,
            )
            story = _build_story(
                context,
                export_result,
                bridge,
                baseline_export_result=baseline_export_result,
            )
            try:
                doc.build(story)
            except OSError as exc:
                raise ExportError(str(exc)) from exc

        atomic_write(path, _write)

    @staticmethod
    def export_simulation_result(
        result: SimulationResult,
        plan_name: str,
        path: Path,
        *,
        display_currency: str = "USD",
        exchange_rates: list[ExchangeRate] | None = None,
    ) -> None:
        """Backward-compatible wrapper until export worker passes ExportContext (Task 21_4)."""
        context = ExportContext(
            plan_name=plan_name,
            result=result,
            entries_summary=EntriesSummary(
                active_income_count=0,
                active_expense_count=0,
                total_line_items=0,
            ),
            exchange_rates=tuple(exchange_rates or ()),
            display_currency=display_currency,
            app_version="",
            exported_at=datetime.now(UTC).isoformat(),
        )
        PdfExporter.export(context, path)
