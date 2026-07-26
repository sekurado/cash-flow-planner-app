from __future__ import annotations

from PySide6.QtCore import (
    Property,
    QAbstractTableModel,
    QByteArray,
    QModelIndex,
    QObject,
    Qt,
    Signal,
)

from src.domain.entities import MonthlySnapshot

_NUM_COLUMNS = 5


def _round_money(value: float) -> float:
    return round(value, 2)


class SnapshotListModel(QAbstractTableModel):
    YEAR_ROLE = Qt.ItemDataRole.UserRole + 1
    MONTH_ROLE = Qt.ItemDataRole.UserRole + 2
    TOTAL_INCOME_ROLE = Qt.ItemDataRole.UserRole + 3
    TOTAL_EXPENSE_ROLE = Qt.ItemDataRole.UserRole + 4
    NET_FLOW_ROLE = Qt.ItemDataRole.UserRole + 5
    CLOSING_BALANCE_ROLE = Qt.ItemDataRole.UserRole + 6
    DEFICIT_ROLE = Qt.ItemDataRole.UserRole + 7

    countChanged = Signal()

    def __init__(
        self,
        snapshots: list[MonthlySnapshot] | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._snapshots: list[MonthlySnapshot] = list(snapshots) if snapshots is not None else []

    @Property(int, notify=countChanged)
    def count(self) -> int:
        return len(self._snapshots)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._snapshots)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]  # noqa: N802
        if parent.isValid():
            return 0
        return _NUM_COLUMNS

    def data(  # type: ignore[override]  # noqa: N802
        self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole
    ) -> object | None:
        if not index.isValid():
            return None
        snapshot = self._snapshots[index.row()]
        match role:
            case self.YEAR_ROLE:
                return snapshot.year
            case self.MONTH_ROLE:
                return snapshot.month
            case self.TOTAL_INCOME_ROLE:
                return _round_money(snapshot.total_income)
            case self.TOTAL_EXPENSE_ROLE:
                return _round_money(snapshot.total_expense)
            case self.NET_FLOW_ROLE:
                return _round_money(snapshot.net_flow)
            case self.CLOSING_BALANCE_ROLE:
                return _round_money(snapshot.closing_balance)
            case self.DEFICIT_ROLE:
                return snapshot.deficit
            case Qt.ItemDataRole.DisplayRole:
                return self._display_value(snapshot, index.column())
            case _:
                return None

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return {
            self.YEAR_ROLE: QByteArray(b"year"),
            self.MONTH_ROLE: QByteArray(b"month"),
            self.TOTAL_INCOME_ROLE: QByteArray(b"totalIncome"),
            self.TOTAL_EXPENSE_ROLE: QByteArray(b"totalExpense"),
            self.NET_FLOW_ROLE: QByteArray(b"netFlow"),
            self.CLOSING_BALANCE_ROLE: QByteArray(b"closingBalance"),
            self.DEFICIT_ROLE: QByteArray(b"deficit"),
            Qt.ItemDataRole.DisplayRole: QByteArray(b"display"),
        }

    def reset(self, snapshots: list[MonthlySnapshot]) -> None:
        self.beginResetModel()
        self._snapshots = list(snapshots)
        self.endResetModel()
        self.countChanged.emit()

    @staticmethod
    def _display_value(snapshot: MonthlySnapshot, column: int) -> object | None:
        match column:
            case 0:
                return snapshot.month
            case 1:
                return _round_money(snapshot.total_income)
            case 2:
                return _round_money(snapshot.total_expense)
            case 3:
                return _round_money(snapshot.net_flow)
            case 4:
                return _round_money(snapshot.closing_balance)
            case _:
                return None
