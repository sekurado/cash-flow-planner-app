from __future__ import annotations

from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from src.app.i18n.user_messages import describe_pattern_text
from src.app.models.entry_list_model import EntryListModel
from src.app.qml_variant import coerce_mapping
from src.app.viewmodels.error_support import ErrorSupport
from src.data.repositories.entry_repo import (
    AbstractEntryRepository,
    EntryCreateDto,
    EntryUpdateDto,
)
from src.domain.date_pattern import parse_pattern
from src.domain.entities import Entry
from src.domain.exceptions import DatePatternParseError


def _entry_to_dict(entry: Entry) -> dict[str, Any]:
    return entry.model_dump()


class EntriesViewModel(QObject):
    """Exposes entry CRUD and date-pattern preview to QML."""

    entriesChanged = Signal()
    entryCreated = Signal(str)
    entryUpdated = Signal(str)
    entryDeleted = Signal(str)
    errorChanged = Signal()

    def __init__(
        self,
        entry_repo: AbstractEntryRepository,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._repo = entry_repo
        self._list_model = EntryListModel(parent=self)
        self._entries: list[dict[str, Any]] = []
        self._errors = ErrorSupport(self)

    @Property("QVariantList", notify=entriesChanged)  # type: ignore[arg-type]
    def entries(self) -> list[dict[str, Any]]:
        return self._entries

    @Property(QObject, constant=True)
    def entryListModel(self) -> EntryListModel:
        return self._list_model

    @Property(str, notify=errorChanged)
    def error(self) -> str:
        return self._errors.message

    @Slot(str)
    def loadEntries(self, plan_id: str) -> None:
        try:
            self._clear_error()
            loaded = self._repo.find_by_plan_id(plan_id)
            self._list_model.reset(loaded)
            self._entries = [_entry_to_dict(entry) for entry in loaded]
            self.entriesChanged.emit()
        except Exception as exc:
            self._set_error(exc)

    @Slot("QVariant")
    def createEntry(self, dto: object) -> None:
        try:
            self._clear_error()
            create_dto = EntryCreateDto.model_validate(
                coerce_mapping(dto, label="Entry create data")
            )
            entry = self._repo.create(create_dto)
            self._list_model.append(entry)
            self._entries.append(_entry_to_dict(entry))
            self.entriesChanged.emit()
            self.entryCreated.emit(entry.id)
        except Exception as exc:
            self._set_error(exc)

    @Slot(str, "QVariant")
    def updateEntry(self, entry_id: str, dto: object) -> None:
        try:
            self._clear_error()
            update_dto = EntryUpdateDto.model_validate(
                coerce_mapping(dto, label="Entry update data")
            )
            updated = self._repo.update(entry_id, update_dto)
            self._list_model.update(entry_id, updated)
            self._entries = [
                _entry_to_dict(updated) if item.get("id") == entry_id else item
                for item in self._entries
            ]
            self.entriesChanged.emit()
            self.entryUpdated.emit(entry_id)
        except Exception as exc:
            self._set_error(exc)

    @Slot(str)
    def deleteEntry(self, entry_id: str) -> None:
        try:
            self._clear_error()
            self._repo.delete(entry_id)
            self._list_model.remove(entry_id)
            self._entries = [item for item in self._entries if item.get("id") != entry_id]
            self.entriesChanged.emit()
            self.entryDeleted.emit(entry_id)
        except Exception as exc:
            self._set_error(exc)

    @Slot(str, result=str)
    def describePattern(self, raw: str) -> str:
        return describe_pattern_text(raw)

    @Slot(str, result=bool)
    def validatePattern(self, raw: str) -> bool:
        try:
            parse_pattern(raw)
        except DatePatternParseError:
            return False
        return True

    @Slot()
    def clearError(self) -> None:
        self._clear_error()

    @Slot()
    def retranslate(self) -> None:
        self._errors.retranslate()

    def _set_error(self, exc: BaseException | str) -> None:
        if isinstance(exc, BaseException):
            self._errors.set_from_exception(exc)
            return
        self._errors.set(exc)

    def _clear_error(self) -> None:
        if not self._errors.clear():
            return
        self.errorChanged.emit()
