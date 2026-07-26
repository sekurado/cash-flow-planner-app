from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, Signal

from src.domain.entities import PlanExportBundle
from src.integrations.plan_import_service import PlanImportService


class PlanImportWorkerSignals(QObject):
    finished = Signal(str)
    error = Signal(str)


class PlanImportWorker(QRunnable):
    """Imports a plan bundle on a background thread."""

    def __init__(
        self,
        import_service: PlanImportService,
        bundle: PlanExportBundle,
        rate_resolutions: dict[str, str],
    ) -> None:
        super().__init__()
        self._import_service = import_service
        self._bundle = bundle
        self._rate_resolutions = rate_resolutions
        self.signals = PlanImportWorkerSignals()

    def run(self) -> None:
        try:
            plan_id = self._import_service.import_bundle(self._bundle, self._rate_resolutions)
            self.signals.finished.emit(plan_id)
        except Exception as exc:
            self.signals.error.emit(str(exc))
