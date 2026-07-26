from __future__ import annotations

from typing import Any

from PySide6.QtCore import Property, QObject, QThreadPool, Signal, Slot

from src.app.qml_variant import coerce_mapping
from src.app.viewmodels.error_support import ErrorSupport
from src.app.workers.import_worker import ImportWorker
from src.data.repositories.entry_repo import AbstractEntryRepository
from src.integrations.import_service import ImportService


class ImportViewModel(QObject):
    """Exposes CSV/Excel import to QML via a background worker."""

    progressChanged = Signal()
    importCompleted = Signal(int, int)
    errorChanged = Signal()
    headersReady = Signal(list)
    previewRowsChanged = Signal()

    def __init__(
        self,
        entry_repo: AbstractEntryRepository,
        import_service: ImportService | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._entry_repo = entry_repo
        self._import_service = import_service or ImportService()
        self._progress = 0.0
        self._imported_count = 0
        self._error_count = 0
        self._errors: list[dict[str, Any]] = []
        self._preview_rows: list[dict[str, Any]] = []
        self._error_state = ErrorSupport(self)
        self._worker: ImportWorker | None = None

    @Property(float, notify=progressChanged)
    def progress(self) -> float:
        return self._progress

    @Property(int, notify=importCompleted)
    def importedCount(self) -> int:
        return self._imported_count

    @Property(int, notify=importCompleted)
    def errorCount(self) -> int:
        return self._error_count

    @Property("QVariantList", notify=importCompleted)  # type: ignore[arg-type]
    def errors(self) -> list[dict[str, Any]]:
        return self._errors

    @Property("QVariantList", notify=previewRowsChanged)  # type: ignore[arg-type]
    def previewRows(self) -> list[dict[str, Any]]:
        return self._preview_rows

    @Property(str, notify=errorChanged)
    def error(self) -> str:
        return self._error_state.message

    @Slot(str)
    def inspectFile(self, path: str) -> None:
        try:
            self._clear_error()
            headers = self._import_service.read_headers(path)
            self.headersReady.emit(headers)
        except Exception as exc:
            self._set_error(exc)

    @Slot(str, "QVariant")
    def updatePreview(self, path: str, column_mapping: object) -> None:
        try:
            self._clear_error()
            mapping = coerce_mapping(column_mapping, label="Column mapping")
            self._preview_rows = self._import_service.read_mapped_preview(path, mapping)
            self.previewRowsChanged.emit()
        except Exception as exc:
            self._set_error(exc)

    @Slot(str, str, "QVariant")
    def importFile(self, path: str, plan_id: str, column_mapping: object) -> None:
        try:
            self._clear_error()
            mapping = coerce_mapping(column_mapping, label="Column mapping")
            self._reset_import_state()
            worker = ImportWorker(
                self._import_service,
                self._entry_repo,
                path,
                plan_id,
                mapping,
            )
            worker.signals.progress.connect(self._on_progress)
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
        self._error_state.retranslate()

    def _reset_import_state(self) -> None:
        self._progress = 0.0
        self._imported_count = 0
        self._error_count = 0
        self._errors = []
        self.progressChanged.emit()

    def _on_progress(self, value: float) -> None:
        self._progress = value
        self.progressChanged.emit()

    def _on_finished(
        self,
        imported_count: int,
        error_count: int,
        errors: list[dict[str, Any]],
    ) -> None:
        self._worker = None
        self._progress = 1.0
        self._imported_count = imported_count
        self._error_count = error_count
        self._errors = errors
        self.progressChanged.emit()
        self.importCompleted.emit(imported_count, error_count)

    def _on_error(self, message: str) -> None:
        self._worker = None
        self._set_error(message)

    def _set_error(self, exc: BaseException | str) -> None:
        if isinstance(exc, BaseException):
            self._error_state.set_from_exception(exc)
            return
        self._error_state.set(exc)

    def _clear_error(self) -> None:
        if not self._error_state.clear():
            return
        self.errorChanged.emit()
