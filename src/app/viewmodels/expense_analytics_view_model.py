from __future__ import annotations

from datetime import date
from typing import Any

from PySide6.QtCore import Property, QObject, QSettings, Signal, Slot

from src.app.viewmodels.error_support import ErrorSupport
from src.app.viewmodels.recorded_expenses_view_model import RecordedExpensesViewModel
from src.data.repositories.exchange_rate_repo import AbstractExchangeRateRepository
from src.data.repositories.recorded_expense_repo import (
    RecordedExpenseAnalyticsRow,
    SqliteRecordedExpenseRepository,
)
from src.domain.expense_analytics import (
    DEFAULT_OTHER_LABEL,
    ExpenseAnalyticsBucket,
    ExpenseAnalyticsEngine,
    ExpenseAnalyticsExpense,
    group_top_n,
)

_TOP_N = 8
_DISPLAY_CURRENCY_KEY = "expenses/display_currency"
_DEFAULT_DISPLAY_CURRENCY = "USD"


def _bucket_to_dict(bucket: ExpenseAnalyticsBucket) -> dict[str, Any]:
    return {
        "label": bucket.label,
        "id": bucket.id or "",
        "totalAmount": bucket.total_amount,
        "transactionCount": bucket.transaction_count,
        "percentOfTotal": bucket.percent_of_total,
    }


def _first_of_month(today: date) -> date:
    return today.replace(day=1)


def _parse_iso_date(value: str, *, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        msg = f"Invalid {field_name}: {value!r}"
        raise ValueError(msg) from exc


class ExpenseAnalyticsViewModel(QObject):
    """Exposes expense analytics rollups and chart series to QML."""

    rollupsChanged = Signal()
    displayCurrencyChanged = Signal()
    dateRangeChanged = Signal()
    errorChanged = Signal()

    def __init__(
        self,
        expense_repo: SqliteRecordedExpenseRepository,
        exchange_rate_repo: AbstractExchangeRateRepository,
        recorded_expenses_vm: RecordedExpensesViewModel,
        *,
        top_n: int = _TOP_N,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._expense_repo = expense_repo
        self._exchange_rate_repo = exchange_rate_repo
        self._top_n = top_n
        self._errors = ErrorSupport(self)
        today = date.today()
        self._start_date = _first_of_month(today)
        self._end_date = today
        saved_currency = QSettings().value(_DISPLAY_CURRENCY_KEY, _DEFAULT_DISPLAY_CURRENCY)
        self._display_currency = (
            saved_currency.strip().upper()
            if isinstance(saved_currency, str) and saved_currency.strip()
            else _DEFAULT_DISPLAY_CURRENCY
        )
        self._total_amount = 0.0
        self._name_series: list[dict[str, Any]] = []
        self._category_series: list[dict[str, Any]] = []
        self._place_series: list[dict[str, Any]] = []

        recorded_expenses_vm.expenseCreated.connect(self._on_expense_mutated)
        recorded_expenses_vm.expenseUpdated.connect(self._on_expense_mutated)
        recorded_expenses_vm.expenseDeleted.connect(self._on_expense_mutated)
        self.refresh()

    @Property(str, notify=displayCurrencyChanged)
    def displayCurrency(self) -> str:
        return self._display_currency

    @Property(str, notify=dateRangeChanged)
    def startDate(self) -> str:
        return self._start_date.isoformat()

    @Property(str, notify=dateRangeChanged)
    def endDate(self) -> str:
        return self._end_date.isoformat()

    @Property(float, notify=rollupsChanged)
    def totalAmount(self) -> float:
        return self._total_amount

    @Property("QVariantList", notify=rollupsChanged)  # type: ignore[arg-type]
    def nameSeries(self) -> list[dict[str, Any]]:
        return self._name_series

    @Property("QVariantList", notify=rollupsChanged)  # type: ignore[arg-type]
    def categorySeries(self) -> list[dict[str, Any]]:
        return self._category_series

    @Property("QVariantList", notify=rollupsChanged)  # type: ignore[arg-type]
    def placeSeries(self) -> list[dict[str, Any]]:
        return self._place_series

    @Property(str, notify=errorChanged)
    def error(self) -> str:
        return self._errors.message

    @Slot(str, str)
    def setDateRange(self, start_iso: str, end_iso: str) -> None:
        try:
            self._clear_error()
            start = _parse_iso_date(start_iso, field_name="start date")
            end = _parse_iso_date(end_iso, field_name="end date")
            if start > end:
                msg = "Start date must be on or before end date"
                raise ValueError(msg)
            if start == self._start_date and end == self._end_date:
                return
            self._start_date = start
            self._end_date = end
            self.dateRangeChanged.emit()
            self.refresh()
        except Exception as exc:
            self._set_error(exc)

    @Slot(str)
    def setDisplayCurrency(self, currency: str) -> None:
        try:
            self._clear_error()
            normalized = currency.strip().upper()
            if not normalized:
                msg = "Display currency is required"
                raise ValueError(msg)
            if normalized == self._display_currency:
                return
            self._display_currency = normalized
            QSettings().setValue(_DISPLAY_CURRENCY_KEY, normalized)
            self.displayCurrencyChanged.emit()
            self.refresh()
        except Exception as exc:
            self._set_error(exc)

    @Slot()
    def refresh(self) -> None:
        try:
            self._clear_error()
            rows = self._expense_repo.list_for_analytics(
                start_date=self._start_date,
                end_date=self._end_date,
            )
            expenses = [_row_to_analytics_expense(row) for row in rows]
            rates = self._exchange_rate_repo.get_all()
            rollups = ExpenseAnalyticsEngine.aggregate(
                expenses,
                start_date=self._start_date,
                end_date=self._end_date,
                display_currency=self._display_currency,
                exchange_rates=rates,
            )
            self._total_amount = rollups.total_amount
            self._name_series = [
                _bucket_to_dict(bucket)
                for bucket in group_top_n(
                    rollups.by_name, self._top_n, other_label=DEFAULT_OTHER_LABEL
                )
            ]
            self._category_series = [
                _bucket_to_dict(bucket)
                for bucket in group_top_n(
                    rollups.by_category,
                    self._top_n,
                    other_label=DEFAULT_OTHER_LABEL,
                )
            ]
            self._place_series = [
                _bucket_to_dict(bucket)
                for bucket in group_top_n(
                    rollups.by_place,
                    self._top_n,
                    other_label=DEFAULT_OTHER_LABEL,
                )
            ]
            self.rollupsChanged.emit()
        except Exception as exc:
            self._set_error(exc)

    @Slot()
    def clearError(self) -> None:
        self._clear_error()

    @Slot()
    def retranslate(self) -> None:
        self._errors.retranslate()

    def _on_expense_mutated(self, _expense_id: str) -> None:
        self.refresh()

    def _set_error(self, exc: BaseException | str) -> None:
        if isinstance(exc, BaseException):
            self._errors.set_from_exception(exc)
            return
        self._errors.set(exc)

    def _clear_error(self) -> None:
        if not self._errors.clear():
            return
        self.errorChanged.emit()


def _row_to_analytics_expense(row: RecordedExpenseAnalyticsRow) -> ExpenseAnalyticsExpense:
    return ExpenseAnalyticsExpense(
        amount=row.amount,
        currency=row.currency,
        occurred_on=row.occurred_on,
        name_id=row.name_id,
        name_label=row.name_label,
        category_id=row.category_id,
        category_label=row.category_label,
        place_id=row.place_id,
        place_label=row.place_label,
    )
