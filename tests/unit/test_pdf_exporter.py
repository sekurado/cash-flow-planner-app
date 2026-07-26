from __future__ import annotations

import stat
from datetime import date
from pathlib import Path

import pytest

from src.app.i18n.pdf_messages import (
    pdf_active_overrides_label,
    pdf_app_version_label,
    pdf_cash_bridge_headers,
    pdf_fx_footnote_headers,
    pdf_fx_normalization_note,
    pdf_methodology_version_label,
    pdf_report_title,
    pdf_scenario_headers,
    pdf_section_balance_chart,
    pdf_section_fx_footnotes,
    pdf_section_monthly_cash_bridge,
    pdf_section_scenario_comparison,
)
from src.domain.entities import (
    DailyBalance,
    ExchangeRate,
    MonthlySnapshot,
    SimulationParams,
    SimulationResult,
)
from src.domain.exceptions import ExportError
from src.export.cash_bridge import build_cash_bridge
from src.export.models import EntriesSummary, ExportContext
from src.export.pdf_colors import DEFICIT_AMBER_BG, EXPENSE_RED, INCOME_GREEN
from src.export.pdf_exporter import (
    PdfExporter,
    _build_story,
    _cash_bridge_table_style,
    _cover_metadata_lines,
    _scenario_comparison_table_style,
    cash_bridge_table_data,
    fx_footnotes_table_data,
    scenario_comparison_table_data,
)


def _sample_result() -> SimulationResult:
    return SimulationResult(
        plan_id="plan-1",
        params=SimulationParams(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            initial_balance=500.0,
            base_currency="USD",
        ),
        daily_balances=(),
        monthly_snapshots=(
            MonthlySnapshot(
                year=2026,
                month=1,
                total_income=1000.0,
                total_expense=400.0,
                net_flow=600.0,
                closing_balance=1100.0,
                deficit=False,
            ),
        ),
        first_deficit_date=None,
        first_deficit_event=None,
        final_balance=1100.0,
        total_income=1000.0,
        total_expense=400.0,
    )


def _sample_context() -> ExportContext:
    result = _sample_result()
    return ExportContext(
        plan_name="Test Forecast",
        result=result,
        entries_summary=EntriesSummary(
            active_income_count=2,
            active_expense_count=1,
            total_line_items=3,
        ),
        exchange_rates=(
            ExchangeRate(
                from_currency="EUR",
                to_currency="USD",
                rate=1.1,
                updated_at="2026-01-01T00:00:00Z",
            ),
        ),
        display_currency="USD",
        app_version="0.1.0",
        exported_at="2026-07-03T12:00:00Z",
    )


@pytest.mark.unit
def test_pdf_export_creates_non_empty_file(tmp_path: Path) -> None:
    output = tmp_path / "report.pdf"

    PdfExporter.export(_sample_context(), output)

    assert output.exists()
    assert output.stat().st_size > 0


@pytest.mark.unit
def test_pdf_export_raises_export_error_for_read_only_directory(tmp_path: Path) -> None:
    read_only_dir = tmp_path / "readonly"
    read_only_dir.mkdir()
    read_only_dir.chmod(stat.S_IREAD | stat.S_IEXEC)

    try:
        with pytest.raises(ExportError):
            PdfExporter.export(_sample_context(), read_only_dir / "report.pdf")
    finally:
        read_only_dir.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)


@pytest.mark.unit
def test_executive_sections_include_metadata_and_cash_bridge() -> None:
    context = _sample_context()
    result = context.result
    bridge = build_cash_bridge(result)
    story_text = " ".join(
        flowable.text
        for flowable in _build_story(context, result, bridge)
        if hasattr(flowable, "text")
    )

    assert pdf_report_title("Test Forecast") in story_text
    assert "Assumptions summary" not in story_text
    assert "Active income cash flows" not in story_text
    assert "Exchange rates applied" not in story_text
    assert pdf_section_monthly_cash_bridge() in story_text
    assert "0.1.0" in _cover_metadata_lines(context)
    assert cash_bridge_table_data(bridge, "USD")[1][2] == "500.00 USD"


@pytest.mark.unit
def test_fx_footnotes_table_data_lists_all_rates() -> None:
    context = _sample_context()
    table = fx_footnotes_table_data(context.exchange_rates)

    assert table[0] == list(pdf_fx_footnote_headers())
    assert table[1] == ["EUR", "USD", "1.1", "2026-01-01T00:00:00Z"]


@pytest.mark.unit
def test_executive_story_includes_fx_footnotes_without_trailing_footer() -> None:
    context = _sample_context()
    result = context.result
    bridge = build_cash_bridge(result)
    story_text = " ".join(
        flowable.text
        for flowable in _build_story(context, result, bridge)
        if hasattr(flowable, "text")
    )

    assert pdf_section_fx_footnotes() in story_text
    assert pdf_fx_normalization_note("USD") in story_text
    assert f"{pdf_methodology_version_label()} 1.0" in _cover_metadata_lines(context)
    assert "See Methodology in Settings" not in story_text
    assert story_text.count(pdf_app_version_label()) == 1


@pytest.mark.unit
def test_executive_story_omits_fx_footnotes_without_rates() -> None:
    context = ExportContext(
        plan_name="No FX Forecast",
        result=_sample_result(),
        entries_summary=EntriesSummary(
            active_income_count=1,
            active_expense_count=1,
            total_line_items=2,
        ),
        exchange_rates=(),
        display_currency="USD",
        app_version="0.1.0",
        exported_at="2026-07-03T12:00:00Z",
    )
    result = context.result
    bridge = build_cash_bridge(result)
    story_text = " ".join(
        flowable.text
        for flowable in _build_story(context, result, bridge)
        if hasattr(flowable, "text")
    )

    assert pdf_section_fx_footnotes() not in story_text
    assert "See Methodology in Settings" not in story_text


@pytest.mark.unit
def test_cash_bridge_table_data_matches_simulation_result() -> None:
    result = _sample_result()
    bridge = build_cash_bridge(result)
    table = cash_bridge_table_data(bridge, "USD")

    assert table[0] == list(pdf_cash_bridge_headers())
    assert table[1] == [
        "2026",
        "1",
        "500.00 USD",
        "1000.00 USD",
        "400.00 USD",
        "600.00 USD",
        "1100.00 USD",
    ]


@pytest.mark.unit
def test_export_simulation_result_wrapper(tmp_path: Path) -> None:
    output = tmp_path / "legacy.pdf"
    result = _sample_result()

    PdfExporter.export_simulation_result(result, "Legacy Forecast", output)

    assert output.exists()
    assert output.stat().st_size > 0


def _baseline_result() -> SimulationResult:
    return SimulationResult(
        plan_id="plan-1",
        params=SimulationParams(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            initial_balance=500.0,
            base_currency="USD",
        ),
        daily_balances=(),
        monthly_snapshots=(),
        first_deficit_date=None,
        first_deficit_event=None,
        final_balance=1000.0,
        total_income=900.0,
        total_expense=400.0,
    )


def _scenario_result() -> SimulationResult:
    return SimulationResult(
        plan_id="plan-1",
        params=SimulationParams(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            initial_balance=500.0,
            base_currency="USD",
        ),
        daily_balances=(),
        monthly_snapshots=(),
        first_deficit_date=date(2026, 1, 15),
        first_deficit_event=None,
        final_balance=800.0,
        total_income=700.0,
        total_expense=400.0,
    )


@pytest.mark.unit
def test_scenario_comparison_table_data_computes_deltas() -> None:
    table = scenario_comparison_table_data(_baseline_result(), _scenario_result(), "USD")

    assert table[0] == list(pdf_scenario_headers())
    assert table[1] == [
        "Final balance",
        "1000.00 USD",
        "800.00 USD",
        "-200.00 USD",
    ]
    assert table[2] == [
        "First cash shortfall date",
        "None",
        "2026-01-15",
        "Only in scenario",
    ]
    assert table[3] == [
        "Total inflows",
        "900.00 USD",
        "700.00 USD",
        "-200.00 USD",
    ]
    assert table[4] == [
        "Total outflows",
        "400.00 USD",
        "400.00 USD",
        "—",
    ]


@pytest.mark.unit
def test_executive_story_omits_scenario_section_without_overrides() -> None:
    context = _sample_context()
    result = context.result
    bridge = build_cash_bridge(result)
    story_text = " ".join(
        flowable.text
        for flowable in _build_story(context, result, bridge)
        if hasattr(flowable, "text")
    )

    assert pdf_section_scenario_comparison() not in story_text


@pytest.mark.unit
def test_executive_story_includes_scenario_section_with_overrides() -> None:
    baseline = _baseline_result()
    scenario = _scenario_result()
    context = ExportContext(
        plan_name="What-if Forecast",
        result=scenario,
        entries_summary=EntriesSummary(
            active_income_count=1,
            active_expense_count=1,
            total_line_items=2,
        ),
        exchange_rates=(),
        display_currency="USD",
        app_version="0.1.0",
        exported_at="2026-07-03T12:00:00Z",
        overrides={"entry-1": {"amount": 50.0}},
        baseline_result=baseline,
        override_footnotes=("Rent: amount → 50.0",),
    )
    bridge = build_cash_bridge(scenario)
    story_text = " ".join(
        flowable.text
        for flowable in _build_story(
            context,
            scenario,
            bridge,
            baseline_export_result=baseline,
        )
        if hasattr(flowable, "text")
    )

    assert pdf_section_scenario_comparison() in story_text
    assert pdf_active_overrides_label() in story_text
    assert "Rent: amount → 50.0" in story_text
    assert scenario_comparison_table_data(baseline, scenario, "USD")[1][3] == "-200.00 USD"


def _result_with_daily_balances() -> SimulationResult:
    return SimulationResult(
        plan_id="plan-1",
        params=SimulationParams(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 5),
            initial_balance=500.0,
            base_currency="USD",
        ),
        daily_balances=(
            DailyBalance(
                date=date(2026, 1, 1),
                events=(),
                day_income=0.0,
                day_expense=0.0,
                closing_balance=500.0,
            ),
            DailyBalance(
                date=date(2026, 1, 2),
                events=(),
                day_income=100.0,
                day_expense=0.0,
                closing_balance=600.0,
            ),
            DailyBalance(
                date=date(2026, 1, 3),
                events=(),
                day_income=0.0,
                day_expense=200.0,
                closing_balance=400.0,
            ),
        ),
        monthly_snapshots=(
            MonthlySnapshot(
                year=2026,
                month=1,
                total_income=100.0,
                total_expense=200.0,
                net_flow=-100.0,
                closing_balance=400.0,
                deficit=False,
            ),
        ),
        first_deficit_date=None,
        first_deficit_event=None,
        final_balance=400.0,
        total_income=100.0,
        total_expense=200.0,
    )


def _deficit_result() -> SimulationResult:
    return SimulationResult(
        plan_id="plan-1",
        params=SimulationParams(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            initial_balance=100.0,
            base_currency="USD",
        ),
        daily_balances=(),
        monthly_snapshots=(
            MonthlySnapshot(
                year=2026,
                month=1,
                total_income=50.0,
                total_expense=200.0,
                net_flow=-150.0,
                closing_balance=-50.0,
                deficit=True,
            ),
        ),
        first_deficit_date=date(2026, 1, 20),
        first_deficit_event=None,
        final_balance=-50.0,
        total_income=50.0,
        total_expense=200.0,
    )


def _table_style_commands(table_style: object) -> list[tuple[object, ...]]:
    return list(getattr(table_style, "_cmds"))  # type: ignore[attr-defined]


@pytest.mark.unit
def test_executive_story_includes_balance_chart_when_daily_data_present() -> None:
    context = ExportContext(
        plan_name="Chart Forecast",
        result=_result_with_daily_balances(),
        entries_summary=EntriesSummary(
            active_income_count=1,
            active_expense_count=1,
            total_line_items=2,
        ),
        exchange_rates=(),
        display_currency="USD",
        app_version="0.1.0",
        exported_at="2026-07-03T12:00:00Z",
    )
    result = context.result
    bridge = build_cash_bridge(result)
    story = _build_story(context, result, bridge)
    story_text = " ".join(flowable.text for flowable in story if hasattr(flowable, "text"))
    drawing_flowables = [flowable for flowable in story if flowable.__class__.__name__ == "Drawing"]

    assert pdf_section_balance_chart() in story_text
    assert drawing_flowables


@pytest.mark.unit
def test_executive_story_omits_balance_chart_without_daily_data() -> None:
    context = _sample_context()
    result = context.result
    bridge = build_cash_bridge(result)
    story = _build_story(context, result, bridge)
    story_text = " ".join(flowable.text for flowable in story if hasattr(flowable, "text"))
    drawing_flowables = [flowable for flowable in story if flowable.__class__.__name__ == "Drawing"]

    assert pdf_section_balance_chart() not in story_text
    assert not drawing_flowables


@pytest.mark.unit
def test_cash_bridge_table_style_applies_semantic_text_colors() -> None:
    result = _sample_result()
    bridge = build_cash_bridge(result)
    table_style = _cash_bridge_table_style(bridge, result)
    commands = _table_style_commands(table_style)
    text_color_commands = [command for command in commands if command[0] == "TEXTCOLOR"]

    assert ("TEXTCOLOR", (3, 1), (3, 1), INCOME_GREEN) in text_color_commands
    assert ("TEXTCOLOR", (4, 1), (4, 1), EXPENSE_RED) in text_color_commands
    assert ("TEXTCOLOR", (5, 1), (5, 1), INCOME_GREEN) in text_color_commands
    assert ("TEXTCOLOR", (6, 1), (6, 1), INCOME_GREEN) in text_color_commands


@pytest.mark.unit
def test_cash_bridge_table_style_highlights_deficit_month_with_amber_background() -> None:
    result = _deficit_result()
    bridge = build_cash_bridge(result)
    table_style = _cash_bridge_table_style(bridge, result)
    commands = _table_style_commands(table_style)

    assert ("BACKGROUND", (0, 1), (-1, 1), DEFICIT_AMBER_BG) in commands


@pytest.mark.unit
def test_scenario_comparison_table_style_colors_money_deltas() -> None:
    baseline = _baseline_result()
    scenario = _scenario_result()
    table_style = _scenario_comparison_table_style(baseline, scenario)
    commands = _table_style_commands(table_style)
    text_color_commands = [command for command in commands if command[0] == "TEXTCOLOR"]

    assert ("TEXTCOLOR", (3, 1), (3, 1), EXPENSE_RED) in text_color_commands
    assert ("TEXTCOLOR", (3, 3), (3, 3), EXPENSE_RED) in text_color_commands


@pytest.mark.unit
def test_executive_pdf_with_chart_is_larger_than_without_chart(tmp_path: Path) -> None:
    context_without_chart = _sample_context()
    context_with_chart = ExportContext(
        plan_name="Chart Forecast",
        result=_result_with_daily_balances(),
        entries_summary=EntriesSummary(
            active_income_count=1,
            active_expense_count=1,
            total_line_items=2,
        ),
        exchange_rates=(),
        display_currency="USD",
        app_version="0.1.0",
        exported_at="2026-07-03T12:00:00Z",
    )
    without_chart = tmp_path / "without-chart.pdf"
    with_chart = tmp_path / "with-chart.pdf"

    PdfExporter.export(context_without_chart, without_chart)
    PdfExporter.export(context_with_chart, with_chart)

    assert with_chart.stat().st_size > without_chart.stat().st_size


@pytest.mark.unit
def test_executive_story_includes_methodology_appendix() -> None:
    context = _sample_context()
    result = context.result
    bridge = build_cash_bridge(result)
    story_text = " ".join(
        flowable.text
        for flowable in _build_story(context, result, bridge)
        if hasattr(flowable, "text")
    )

    assert "Methodology" in story_text
    assert "Methodology version:" in story_text
    assert "Cash shortfall detection" in story_text
