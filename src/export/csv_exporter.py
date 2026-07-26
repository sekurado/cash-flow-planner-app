from __future__ import annotations

import csv
from pathlib import Path

from src.domain.entities import ExchangeRate, MonthlySnapshot, SimulationResult
from src.export._atomic import atomic_write
from src.export._display_currency import convert_result_for_display
from src.export.metadata import ExportMetadata, build_export_metadata, metadata_csv_comment_lines

_FIELDNAMES = ("Year", "Month", "Income", "Expense", "Net", "Balance", "Shortfall")


def _round_money(value: float) -> float:
    return round(value, 2)


def _snapshot_row(snapshot: MonthlySnapshot) -> dict[str, object]:
    return {
        "Year": snapshot.year,
        "Month": snapshot.month,
        "Income": _round_money(snapshot.total_income),
        "Expense": _round_money(snapshot.total_expense),
        "Net": _round_money(snapshot.net_flow),
        "Balance": _round_money(snapshot.closing_balance),
        "Shortfall": snapshot.deficit,
    }


class CsvExporter:
    @staticmethod
    def export(
        result: SimulationResult,
        path: Path,
        *,
        display_currency: str = "USD",
        exchange_rates: list[ExchangeRate] | None = None,
        metadata: ExportMetadata | None = None,
        app_version: str = "",
    ) -> None:
        export_result = result
        if display_currency != result.params.base_currency and exchange_rates is not None:
            export_result = convert_result_for_display(result, display_currency, exchange_rates)

        export_metadata = metadata or build_export_metadata(
            app_version=app_version,
            display_currency=display_currency,
            exchange_rates=exchange_rates,
        )

        def _write(target: Path) -> None:
            with target.open("w", newline="", encoding="utf-8") as file:
                for line in metadata_csv_comment_lines(export_metadata):
                    file.write(f"{line}\n")
                writer = csv.DictWriter(file, fieldnames=_FIELDNAMES)
                writer.writeheader()
                for snapshot in export_result.monthly_snapshots:
                    writer.writerow(_snapshot_row(snapshot))

        atomic_write(path, _write)
