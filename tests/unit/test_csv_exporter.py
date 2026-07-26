from __future__ import annotations

import csv
import stat
from datetime import date
from pathlib import Path

import pytest

from src.domain.entities import MonthlySnapshot, SimulationParams, SimulationResult
from src.domain.exceptions import ExportError
from src.export.csv_exporter import CsvExporter

_BASE_CURRENCY = "USD"


def _read_csv_data_rows(path: Path) -> list[list[str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return [row for row in csv.reader(file) if row and not row[0].startswith("#")]


def _snapshot(
    *,
    year: int,
    month: int,
    total_income: float,
    total_expense: float,
    closing_balance: float,
    deficit: bool = False,
) -> MonthlySnapshot:
    return MonthlySnapshot(
        year=year,
        month=month,
        total_income=total_income,
        total_expense=total_expense,
        net_flow=total_income - total_expense,
        closing_balance=closing_balance,
        deficit=deficit,
    )


def _sample_result() -> SimulationResult:
    return SimulationResult(
        plan_id="plan-1",
        params=SimulationParams(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
            initial_balance=1000.0,
            base_currency=_BASE_CURRENCY,
        ),
        daily_balances=(),
        monthly_snapshots=(
            _snapshot(
                year=2026,
                month=1,
                total_income=2000.0,
                total_expense=1500.0,
                closing_balance=1500.0,
            ),
            _snapshot(
                year=2026,
                month=2,
                total_income=2000.0,
                total_expense=1800.0,
                closing_balance=1700.0,
                deficit=True,
            ),
            _snapshot(
                year=2026,
                month=3,
                total_income=2100.0,
                total_expense=1600.0,
                closing_balance=2200.0,
            ),
        ),
        first_deficit_date=date(2026, 2, 28),
        first_deficit_event=None,
        final_balance=2200.0,
        total_income=6100.0,
        total_expense=4900.0,
    )


@pytest.mark.unit
def test_csv_export_row_count_matches_monthly_snapshots(tmp_path: Path) -> None:
    result = _sample_result()
    output = tmp_path / "report.csv"

    CsvExporter.export(result, output)

    rows = _read_csv_data_rows(output)
    assert len(rows) - 1 == len(result.monthly_snapshots)


@pytest.mark.unit
def test_csv_export_header_columns(tmp_path: Path) -> None:
    result = _sample_result()
    output = tmp_path / "report.csv"

    CsvExporter.export(result, output)

    rows = _read_csv_data_rows(output)
    assert rows[0] == ["Year", "Month", "Income", "Expense", "Net", "Balance", "Shortfall"]


@pytest.mark.unit
def test_csv_export_income_values_match_snapshots(tmp_path: Path) -> None:
    result = _sample_result()
    output = tmp_path / "report.csv"

    CsvExporter.export(result, output, app_version="0.1.0")

    with output.open(newline="", encoding="utf-8") as file:
        lines = file.readlines()
    comment_lines = [line.strip() for line in lines if line.startswith("#")]
    assert any(line.startswith("# app_version: ") for line in comment_lines)
    assert any(line.startswith("# exported_at: ") for line in comment_lines)

    with output.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(row for row in file if not row.startswith("#"))
        incomes = [float(row["Income"]) for row in reader]
    expected = [round(snapshot.total_income, 2) for snapshot in result.monthly_snapshots]
    assert incomes == expected


@pytest.mark.unit
def test_csv_export_raises_export_error_for_read_only_directory(tmp_path: Path) -> None:
    read_only_dir = tmp_path / "readonly"
    read_only_dir.mkdir()
    read_only_dir.chmod(stat.S_IREAD | stat.S_IEXEC)
    result = _sample_result()

    try:
        with pytest.raises(ExportError):
            CsvExporter.export(result, read_only_dir / "report.csv")
    finally:
        read_only_dir.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
