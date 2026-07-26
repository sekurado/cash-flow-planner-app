from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, Signal

from src.app.workers.simulation_worker import (
    JsonValue,
    deserialize_simulation_result,
    run_plan_simulation,
)
from src.data.repositories.entry_repo import AbstractEntryRepository
from src.data.repositories.exchange_rate_repo import AbstractExchangeRateRepository
from src.domain.entities import ExchangeRate
from src.export.context_builder import (
    build_entries_summary,
    build_override_footnotes,
)
from src.export.csv_exporter import CsvExporter
from src.export.metadata import build_export_metadata
from src.export.models import ExportContext
from src.export.pdf_exporter import PdfExporter
from src.export.rate_selection import rates_used_for_export


class ExportFormat(StrEnum):
    CSV = "csv"
    PDF = "pdf"


class ExportWorkerSignals(QObject):
    finished = Signal()
    error = Signal(str)


class ExportWorker(QRunnable):
    """Runs a simulation export on a background thread."""

    def __init__(
        self,
        result: dict[str, JsonValue],
        file_path: str,
        export_format: ExportFormat,
        *,
        plan_name: str = "",
        display_currency: str = "USD",
        exchange_rates: list[ExchangeRate] | None = None,
        plan_id: str = "",
        entry_repo: AbstractEntryRepository | None = None,
        exchange_rate_repo: AbstractExchangeRateRepository | None = None,
        overrides: dict[str, dict[str, object]] | None = None,
        app_version: str = "",
    ) -> None:
        super().__init__()
        self._result = result
        self._file_path = file_path
        self._export_format = export_format
        self._plan_name = plan_name
        self._display_currency = display_currency
        self._exchange_rates = exchange_rates or []
        self._plan_id = plan_id
        self._entry_repo = entry_repo
        self._exchange_rate_repo = exchange_rate_repo
        self._overrides = overrides
        self._app_version = app_version
        self.signals = ExportWorkerSignals()

    def run(self) -> None:
        try:
            simulation_result = deserialize_simulation_result(self._result)
            path = Path(self._file_path)
            if self._export_format is ExportFormat.CSV:
                CsvExporter.export(
                    simulation_result,
                    path,
                    display_currency=self._display_currency,
                    exchange_rates=self._exchange_rates,
                    metadata=build_export_metadata(
                        app_version=self._app_version,
                        display_currency=self._display_currency,
                        exchange_rates=self._exchange_rates,
                    )
                    if self._app_version
                    else None,
                    app_version=self._app_version,
                )
            elif self._can_build_executive_context():
                context = self._build_executive_context(simulation_result)
                PdfExporter.export(context, path)
            else:
                filtered_rates = list(
                    rates_used_for_export(
                        entry_currencies=(),
                        base_currency=simulation_result.params.base_currency,
                        display_currency=self._display_currency,
                        exchange_rates=self._exchange_rates,
                    )
                )
                PdfExporter.export_simulation_result(
                    simulation_result,
                    self._plan_name,
                    path,
                    display_currency=self._display_currency,
                    exchange_rates=filtered_rates,
                )
            self.signals.finished.emit()
        except Exception as exc:
            self.signals.error.emit(str(exc))

    def _can_build_executive_context(self) -> bool:
        return (
            self._export_format is ExportFormat.PDF
            and self._entry_repo is not None
            and self._exchange_rate_repo is not None
            and bool(self._plan_id)
        )

    def _build_executive_context(self, scenario_result: object) -> ExportContext:
        from src.domain.entities import SimulationResult

        assert isinstance(scenario_result, SimulationResult)
        assert self._entry_repo is not None
        assert self._exchange_rate_repo is not None

        entries = self._entry_repo.find_by_plan_id(self._plan_id)
        baseline_result: SimulationResult | None = None
        override_footnotes: tuple[str, ...] = ()
        if self._overrides:
            baseline_result = run_plan_simulation(
                self._entry_repo,
                self._exchange_rate_repo,
                self._plan_id,
                scenario_result.params,
                what_if_overrides=None,
            )
            override_footnotes = build_override_footnotes(entries, self._overrides)

        from src.app.workers.simulation_worker import prepare_entries

        scenario_entries = prepare_entries(entries, self._overrides)
        base_currency = scenario_result.params.base_currency
        filtered_rates = rates_used_for_export(
            entry_currencies={entry.currency for entry in scenario_entries},
            base_currency=base_currency,
            display_currency=self._display_currency,
            exchange_rates=self._exchange_rates,
        )
        return ExportContext(
            plan_name=self._plan_name,
            result=scenario_result,
            entries_summary=build_entries_summary(scenario_entries),
            exchange_rates=filtered_rates,
            display_currency=self._display_currency,
            app_version=self._app_version,
            exported_at=datetime.now(UTC).isoformat(),
            overrides=self._overrides,
            baseline_result=baseline_result,
            override_footnotes=override_footnotes,
        )
