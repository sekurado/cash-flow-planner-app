from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Property, QObject, QThreadPool, Signal, Slot

from src.app.viewmodels.error_support import ErrorSupport
from src.app.workers.plan_import_worker import PlanImportWorker
from src.domain.entities import PlanExportBundle, PlanImportPreview
from src.integrations.plan_import_service import PlanImportService

_DEFAULT_RESOLUTION = "keep"


class PlanImportViewModel(QObject):
    """Exposes .ftplan import preview and background import to QML."""

    previewReady = Signal()
    rateConflictsChanged = Signal()
    importCompleted = Signal(str)
    isImportingChanged = Signal()
    errorChanged = Signal()

    def __init__(
        self,
        import_service: PlanImportService,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._import_service = import_service
        self._errors = ErrorSupport(self)
        self._worker: PlanImportWorker | None = None
        self._preview_name = ""
        self._preview_entry_count = 0
        self._preview_currencies: list[str] = []
        self._rate_additions: list[dict[str, Any]] = []
        self._rate_conflicts: list[dict[str, Any]] = []
        self._preview_bundle: PlanExportBundle | None = None
        self._inspected_path = ""
        self._is_importing = False

    @Property(str, notify=previewReady)
    def previewName(self) -> str:
        return self._preview_name

    @Property(int, notify=previewReady)
    def previewEntryCount(self) -> int:
        return self._preview_entry_count

    @Property("QVariantList", notify=previewReady)  # type: ignore[arg-type]
    def previewCurrencies(self) -> list[str]:
        return self._preview_currencies

    @Property("QVariantList", notify=previewReady)  # type: ignore[arg-type]
    def rateAdditions(self) -> list[dict[str, Any]]:
        return self._rate_additions

    @Property("QVariantList", notify=rateConflictsChanged)  # type: ignore[arg-type]
    def rateConflicts(self) -> list[dict[str, Any]]:
        return self._rate_conflicts

    @Property(bool, notify=previewReady)
    def hasRateConflicts(self) -> bool:
        return bool(self._rate_conflicts)

    @Property(bool, notify=isImportingChanged)
    def isImporting(self) -> bool:
        return self._is_importing

    @Property(str, notify=errorChanged)
    def error(self) -> str:
        return self._errors.message

    @Slot(str)
    def inspectFile(self, path: str) -> None:
        try:
            self._clear_error()
            normalized_path = str(Path(path))
            preview = self._import_service.inspect(Path(normalized_path))
            self._apply_preview(preview)
            self._inspected_path = normalized_path
            self.previewReady.emit()
            self.rateConflictsChanged.emit()
        except Exception as exc:
            self._set_error(exc)

    @Slot(str, str)
    def setRateResolution(self, from_currency: str, resolution: str) -> None:
        updated = False
        for conflict in self._rate_conflicts:
            if conflict["fromCurrency"] == from_currency:
                conflict["resolution"] = resolution
                updated = True
        if updated:
            self.rateConflictsChanged.emit()

    @Slot(str)
    def setAllRateResolutions(self, resolution: str) -> None:
        if not self._rate_conflicts:
            return
        for conflict in self._rate_conflicts:
            conflict["resolution"] = resolution
        self.rateConflictsChanged.emit()

    @Slot(str)
    def importFile(self, path: str) -> None:
        try:
            self._clear_error()
            normalized_path = str(Path(path))
            if self._preview_bundle is None or self._inspected_path != normalized_path:
                preview = self._import_service.inspect(Path(normalized_path))
                self._apply_preview(preview)
                self._inspected_path = normalized_path
            bundle = self._preview_bundle
            if bundle is None:
                msg = "No import preview is available for this file"
                raise ValueError(msg)
            rate_resolutions = {
                conflict["fromCurrency"]: conflict["resolution"]
                for conflict in self._rate_conflicts
            }
            self._is_importing = True
            self.isImportingChanged.emit()
            worker = PlanImportWorker(
                self._import_service,
                bundle,
                rate_resolutions,
            )
            worker.signals.finished.connect(self._on_finished)
            worker.signals.error.connect(self._on_error)
            self._worker = worker
            QThreadPool.globalInstance().start(worker)
        except Exception as exc:
            self._set_error(exc)

    @Slot()
    def clearError(self) -> None:
        self._clear_error()

    @Slot()
    def retranslate(self) -> None:
        self._errors.retranslate()

    def _apply_preview(self, preview: PlanImportPreview) -> None:
        bundle = preview.bundle
        self._preview_bundle = bundle
        self._preview_name = bundle.plan.name
        self._preview_entry_count = len(bundle.entries)
        self._preview_currencies = sorted({entry.currency for entry in bundle.entries})
        self._rate_additions = [
            {"fromCurrency": rate.from_currency, "rate": rate.rate}
            for rate in preview.rate_additions
        ]
        self._rate_conflicts = [
            {
                "fromCurrency": conflict.from_currency,
                "localRate": conflict.local_rate,
                "fileRate": conflict.file_rate,
                "resolution": _DEFAULT_RESOLUTION,
            }
            for conflict in preview.rate_conflicts
        ]

    def _on_finished(self, plan_id: str) -> None:
        self._worker = None
        self._is_importing = False
        self.isImportingChanged.emit()
        self.importCompleted.emit(plan_id)

    def _on_error(self, message: str) -> None:
        self._worker = None
        self._is_importing = False
        self.isImportingChanged.emit()
        self._set_error(message)

    def _set_error(self, exc: BaseException | str) -> None:
        if isinstance(exc, BaseException):
            self._errors.set_from_exception(exc)
            return
        self._errors.set(exc)

    def _clear_error(self) -> None:
        if not self._errors.clear():
            return
        self.errorChanged.emit()
