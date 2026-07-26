from __future__ import annotations

from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from src.app.i18n.audit_log_messages import translate_audit_summary
from src.app.viewmodels.error_support import ErrorSupport
from src.data.repositories.audit_log_repo import AbstractAuditLogRepository
from src.domain.entities import AuditLogEntry


def _entry_to_dict(entry: AuditLogEntry) -> dict[str, Any]:
    data = entry.model_dump()
    data["summary"] = translate_audit_summary(entry.summary)
    return data


class AuditLogViewModel(QObject):
    """Exposes read-only audit log entries for a forecast to QML."""

    entriesChanged = Signal()
    errorChanged = Signal()

    def __init__(
        self,
        audit_log_repo: AbstractAuditLogRepository,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._repo = audit_log_repo
        self._raw_entries: list[AuditLogEntry] = []
        self._entries: list[dict[str, Any]] = []
        self._errors = ErrorSupport(self)

    @Property("QVariantList", notify=entriesChanged)  # type: ignore[arg-type]
    def entries(self) -> list[dict[str, Any]]:
        return self._entries

    @Property(str, notify=errorChanged)
    def error(self) -> str:
        return self._errors.message

    @Slot(str)
    def loadForPlan(self, plan_id: str) -> None:
        try:
            self._clear_error()
            loaded = self._repo.list_by_plan(plan_id)
            self._raw_entries = loaded
            self._entries = [_entry_to_dict(entry) for entry in loaded]
            self.entriesChanged.emit()
        except Exception as exc:
            self._set_error(exc)

    @Slot()
    def clearError(self) -> None:
        self._clear_error()

    @Slot()
    def retranslate(self) -> None:
        self._errors.retranslate()
        if not self._raw_entries:
            return
        self._entries = [_entry_to_dict(entry) for entry in self._raw_entries]
        self.entriesChanged.emit()

    def _set_error(self, exc: BaseException | str) -> None:
        if isinstance(exc, BaseException):
            self._errors.set_from_exception(exc)
            return
        self._errors.set(exc)

    def _clear_error(self) -> None:
        if not self._errors.clear():
            return
        self.errorChanged.emit()
