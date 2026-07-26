from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

import pytest

from src.domain.entities import ExchangeRate, MonthlySnapshot, SimulationParams, SimulationResult
from src.export.csv_exporter import CsvExporter

_BASE_CURRENCY = "USD"


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
            end_date=date(2026, 1, 31),
            initial_balance=0.0,
            base_currency=_BASE_CURRENCY,
        ),
        daily_balances=(),
        monthly_snapshots=(
            _snapshot(
                year=2026,
                month=1,
                total_income=1100.0,
                total_expense=0.0,
                closing_balance=1100.0,
            ),
        ),
        first_deficit_date=None,
        first_deficit_event=None,
        final_balance=1100.0,
        total_income=1100.0,
        total_expense=0.0,
    )


@pytest.mark.unit
def test_csv_export_converts_to_display_currency(tmp_path: Path) -> None:
    result = _sample_result()
    output = tmp_path / "report.csv"
    rates = [
        ExchangeRate(
            from_currency="EUR",
            to_currency="USD",
            rate=1.1,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    ]

    CsvExporter.export(result, output, display_currency="EUR", exchange_rates=rates)

    with output.open(newline="", encoding="utf-8") as file:
        row = next(csv.DictReader(row for row in file if not row.startswith("#")))
    assert float(row["Income"]) == pytest.approx(1000.0)


@pytest.mark.unit
def test_csv_export_converts_from_eur_base_to_display_currency(tmp_path: Path) -> None:
    result = SimulationResult(
        plan_id="plan-eur",
        params=SimulationParams(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            initial_balance=0.0,
            base_currency="EUR",
        ),
        daily_balances=(),
        monthly_snapshots=(
            _snapshot(
                year=2026,
                month=1,
                total_income=920.0,
                total_expense=0.0,
                closing_balance=920.0,
            ),
        ),
        first_deficit_date=None,
        first_deficit_event=None,
        final_balance=920.0,
        total_income=920.0,
        total_expense=0.0,
    )
    output = tmp_path / "report-eur.csv"
    rates = [
        ExchangeRate(
            from_currency="USD",
            to_currency="EUR",
            rate=0.92,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    ]

    CsvExporter.export(result, output, display_currency="USD", exchange_rates=rates)

    with output.open(newline="", encoding="utf-8") as file:
        row = next(csv.DictReader(row for row in file if not row.startswith("#")))
    assert float(row["Income"]) == pytest.approx(1000.0)
