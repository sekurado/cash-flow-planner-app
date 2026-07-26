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

from src.domain.entities import ExchangeRate


class ExchangeRateListModel(QAbstractListModel):
    FROM_CURRENCY_ROLE = Qt.ItemDataRole.UserRole + 1
    TO_CURRENCY_ROLE = Qt.ItemDataRole.UserRole + 2
    RATE_ROLE = Qt.ItemDataRole.UserRole + 3
    UPDATED_AT_ROLE = Qt.ItemDataRole.UserRole + 4

    countChanged = Signal()

    def __init__(
        self,
        rates: list[ExchangeRate] | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._rates: list[ExchangeRate] = list(rates) if rates is not None else []

    @Property(int, notify=countChanged)
    def count(self) -> int:
        return len(self._rates)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._rates)

    def data(  # type: ignore[override]  # noqa: N802
        self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole
    ) -> object | None:
        if not index.isValid():
            return None
        rate = self._rates[index.row()]
        match role:
            case self.FROM_CURRENCY_ROLE:
                return rate.from_currency
            case self.TO_CURRENCY_ROLE:
                return rate.to_currency
            case self.RATE_ROLE:
                return rate.rate
            case self.UPDATED_AT_ROLE:
                return rate.updated_at
            case _:
                return None

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return {
            self.FROM_CURRENCY_ROLE: QByteArray(b"fromCurrency"),
            self.TO_CURRENCY_ROLE: QByteArray(b"toCurrency"),
            self.RATE_ROLE: QByteArray(b"rate"),
            self.UPDATED_AT_ROLE: QByteArray(b"updatedAt"),
        }

    def reset(self, rates: list[ExchangeRate]) -> None:
        self.beginResetModel()
        self._rates = list(rates)
        self.endResetModel()
        self.countChanged.emit()

    def append(self, rate: ExchangeRate) -> None:
        row = len(self._rates)
        self.beginInsertRows(QModelIndex(), row, row)
        self._rates.append(rate)
        self.endInsertRows()
        self.countChanged.emit()

    def remove(self, from_currency: str, to_currency: str) -> None:
        for index, rate in enumerate(self._rates):
            if rate.from_currency == from_currency and rate.to_currency == to_currency:
                self.beginRemoveRows(QModelIndex(), index, index)
                del self._rates[index]
                self.endRemoveRows()
                self.countChanged.emit()
                return

    def update(self, from_currency: str, to_currency: str, rate: ExchangeRate) -> None:
        for index, existing in enumerate(self._rates):
            if existing.from_currency == from_currency and existing.to_currency == to_currency:
                self._rates[index] = rate
                model_index = self.index(index, 0)
                self.dataChanged.emit(model_index, model_index)
                return
