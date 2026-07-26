from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, QObject, Qt

from src.domain.entities import Entry


class EntryListModel(QAbstractListModel):
    ID_ROLE = Qt.ItemDataRole.UserRole + 1
    NAME_ROLE = Qt.ItemDataRole.UserRole + 2
    DATE_PATTERN_ROLE = Qt.ItemDataRole.UserRole + 3
    AMOUNT_ROLE = Qt.ItemDataRole.UserRole + 4
    CURRENCY_ROLE = Qt.ItemDataRole.UserRole + 5
    TYPE_ROLE = Qt.ItemDataRole.UserRole + 6
    CATEGORY_ROLE = Qt.ItemDataRole.UserRole + 7
    IS_ACTIVE_ROLE = Qt.ItemDataRole.UserRole + 8

    def __init__(
        self,
        entries: list[Entry] | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._entries: list[Entry] = list(entries) if entries is not None else []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._entries)

    def data(  # type: ignore[override]  # noqa: N802
        self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole
    ) -> object | None:
        if not index.isValid():
            return None
        entry = self._entries[index.row()]
        match role:
            case self.ID_ROLE:
                return entry.id
            case self.NAME_ROLE:
                return entry.name
            case self.DATE_PATTERN_ROLE:
                return entry.date_pattern
            case self.AMOUNT_ROLE:
                return entry.amount
            case self.CURRENCY_ROLE:
                return entry.currency
            case self.TYPE_ROLE:
                return entry.entry_type.value
            case self.CATEGORY_ROLE:
                return entry.category or ""
            case self.IS_ACTIVE_ROLE:
                return entry.is_active
            case _:
                return None

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return {
            self.ID_ROLE: QByteArray(b"entryId"),
            self.NAME_ROLE: QByteArray(b"name"),
            self.DATE_PATTERN_ROLE: QByteArray(b"datePattern"),
            self.AMOUNT_ROLE: QByteArray(b"amount"),
            self.CURRENCY_ROLE: QByteArray(b"currency"),
            self.TYPE_ROLE: QByteArray(b"entryType"),
            self.CATEGORY_ROLE: QByteArray(b"category"),
            self.IS_ACTIVE_ROLE: QByteArray(b"isActive"),
        }

    def reset(self, entries: list[Entry]) -> None:
        self.beginResetModel()
        self._entries = list(entries)
        self.endResetModel()

    def append(self, entry: Entry) -> None:
        row = len(self._entries)
        self.beginInsertRows(QModelIndex(), row, row)
        self._entries.append(entry)
        self.endInsertRows()

    def remove(self, entry_id: str) -> None:
        for index, entry in enumerate(self._entries):
            if entry.id == entry_id:
                self.beginRemoveRows(QModelIndex(), index, index)
                del self._entries[index]
                self.endRemoveRows()
                return

    def update(self, entry_id: str, entry: Entry) -> None:
        for index, existing in enumerate(self._entries):
            if existing.id == entry_id:
                self._entries[index] = entry
                model_index = self.index(index, 0)
                self.dataChanged.emit(model_index, model_index)
                return
