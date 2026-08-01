from __future__ import annotations

from PySide6.QtCore import (
    Property,
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    QObject,
    Qt,
    Signal,
)

from src.data.repositories.recorded_expense_repo import RecordedExpenseListItem


class RecordedExpenseListModel(QAbstractListModel):
    EXPENSE_ID_ROLE = Qt.ItemDataRole.UserRole + 1
    AMOUNT_ROLE = Qt.ItemDataRole.UserRole + 2
    CURRENCY_ROLE = Qt.ItemDataRole.UserRole + 3
    OCCURRED_ON_ROLE = Qt.ItemDataRole.UserRole + 4
    NAME_LABEL_ROLE = Qt.ItemDataRole.UserRole + 5
    CATEGORY_LABEL_ROLE = Qt.ItemDataRole.UserRole + 6
    PLACE_LABEL_ROLE = Qt.ItemDataRole.UserRole + 7
    NOTE_ROLE = Qt.ItemDataRole.UserRole + 8

    countChanged = Signal()

    def __init__(
        self,
        expenses: list[RecordedExpenseListItem] | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._expenses: list[RecordedExpenseListItem] = (
            list(expenses) if expenses is not None else []
        )

    @Property(int, notify=countChanged)
    def count(self) -> int:
        return len(self._expenses)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._expenses)

    def data(  # type: ignore[override]  # noqa: N802
        self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole
    ) -> object | None:
        if not index.isValid():
            return None
        expense = self._expenses[index.row()]
        match role:
            case self.EXPENSE_ID_ROLE:
                return expense.id
            case self.AMOUNT_ROLE:
                return expense.amount
            case self.CURRENCY_ROLE:
                return expense.currency
            case self.OCCURRED_ON_ROLE:
                return expense.occurred_on.isoformat()
            case self.NAME_LABEL_ROLE:
                return expense.name_label
            case self.CATEGORY_LABEL_ROLE:
                return expense.category_label or ""
            case self.PLACE_LABEL_ROLE:
                return expense.place_label or ""
            case self.NOTE_ROLE:
                return expense.note or ""
            case _:
                return None

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return {
            self.EXPENSE_ID_ROLE: QByteArray(b"expenseId"),
            self.AMOUNT_ROLE: QByteArray(b"amount"),
            self.CURRENCY_ROLE: QByteArray(b"currency"),
            self.OCCURRED_ON_ROLE: QByteArray(b"occurredOn"),
            self.NAME_LABEL_ROLE: QByteArray(b"nameLabel"),
            self.CATEGORY_LABEL_ROLE: QByteArray(b"categoryLabel"),
            self.PLACE_LABEL_ROLE: QByteArray(b"placeLabel"),
            self.NOTE_ROLE: QByteArray(b"note"),
        }

    def reset(self, expenses: list[RecordedExpenseListItem]) -> None:
        self.beginResetModel()
        self._expenses = list(expenses)
        self.endResetModel()
        self.countChanged.emit()
