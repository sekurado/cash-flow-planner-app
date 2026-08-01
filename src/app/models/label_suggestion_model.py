from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import (
    Property,
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    QObject,
    Qt,
    Signal,
)


@dataclass(frozen=True)
class LabelSuggestion:
    id: str
    label: str


class LabelSuggestionModel(QAbstractListModel):
    ID_ROLE = Qt.ItemDataRole.UserRole + 1
    LABEL_ROLE = Qt.ItemDataRole.UserRole + 2

    countChanged = Signal()

    def __init__(
        self,
        suggestions: list[LabelSuggestion] | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._suggestions: list[LabelSuggestion] = (
            list(suggestions) if suggestions is not None else []
        )

    @Property(int, notify=countChanged)
    def count(self) -> int:
        return len(self._suggestions)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._suggestions)

    def data(  # type: ignore[override]  # noqa: N802
        self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole
    ) -> object | None:
        if not index.isValid():
            return None
        suggestion = self._suggestions[index.row()]
        match role:
            case self.ID_ROLE:
                return suggestion.id
            case self.LABEL_ROLE:
                return suggestion.label
            case _:
                return None

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return {
            self.ID_ROLE: QByteArray(b"labelId"),
            self.LABEL_ROLE: QByteArray(b"label"),
        }

    def reset(self, suggestions: list[LabelSuggestion]) -> None:
        self.beginResetModel()
        self._suggestions = list(suggestions)
        self.endResetModel()
        self.countChanged.emit()
