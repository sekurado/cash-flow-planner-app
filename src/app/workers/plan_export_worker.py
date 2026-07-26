from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, Signal

from src.export.plan_exporter import PlanExporter


class PlanExportWorkerSignals(QObject):
    finished = Signal()
    error = Signal(str)


class PlanExportWorker(QRunnable):
    """Exports a plan bundle to a .ftplan file on a background thread."""

    def __init__(
        self,
        exporter: PlanExporter,
        plan_id: str,
        file_path: str,
        *,
        app_version: str = "",
    ) -> None:
        super().__init__()
        self._exporter = exporter
        self._plan_id = plan_id
        self._file_path = file_path
        self._app_version = app_version
        self.signals = PlanExportWorkerSignals()

    def run(self) -> None:
        try:
            self._exporter.export(
                self._plan_id,
                Path(self._file_path),
                app_version=self._app_version,
            )
            self.signals.finished.emit()
        except Exception as exc:
            self.signals.error.emit(str(exc))
