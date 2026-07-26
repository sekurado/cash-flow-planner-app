from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, Signal

from src.data.repositories.entry_repo import AbstractEntryRepository, EntryCreateDto
from src.integrations.import_service import ImportService

_IMPORT_BATCH_SIZE = 10


class ImportWorkerSignals(QObject):
    progress = Signal(float)
    finished = Signal(int, int, list)
    error = Signal(str)


class ImportWorker(QRunnable):
    """Parses an import file and inserts valid rows in batches on a background thread."""

    def __init__(
        self,
        import_service: ImportService,
        entry_repo: AbstractEntryRepository,
        path: str,
        plan_id: str,
        column_mapping: dict[str, str],
        *,
        batch_size: int = _IMPORT_BATCH_SIZE,
    ) -> None:
        super().__init__()
        self._import_service = import_service
        self._entry_repo = entry_repo
        self._path = path
        self._plan_id = plan_id
        self._column_mapping = column_mapping
        self._batch_size = batch_size
        self.signals = ImportWorkerSignals()

    def run(self) -> None:
        try:
            result = self._import_service.parse(self._path, self._column_mapping)
            row_errors = [
                {"row": error.row_number, "message": error.error_message} for error in result.errors
            ]
            valid_rows = result.valid_rows
            total = len(valid_rows)

            if total == 0:
                self.signals.progress.emit(1.0)
                self.signals.finished.emit(0, len(row_errors), row_errors)
                return

            imported = 0
            for start in range(0, total, self._batch_size):
                batch = valid_rows[start : start + self._batch_size]
                for row in batch:
                    self._entry_repo.create(
                        EntryCreateDto(
                            plan_id=self._plan_id,
                            entry_type=row.entry_type,
                            name=row.name,
                            date_pattern=row.date_pattern,
                            amount=row.amount,
                            currency=row.currency,
                            category=row.category,
                            is_active=row.is_active,
                        )
                    )
                    imported += 1
                self.signals.progress.emit(imported / total)

            self.signals.progress.emit(1.0)
            self.signals.finished.emit(imported, len(row_errors), row_errors)
        except Exception as exc:
            self.signals.error.emit(str(exc))
