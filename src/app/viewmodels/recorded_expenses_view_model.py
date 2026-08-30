from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from PySide6.QtCore import Property, QObject, QThreadPool, QTimer, Signal, Slot

from src.app.models.label_suggestion_model import LabelSuggestion, LabelSuggestionModel
from src.app.models.recorded_expense_list_model import RecordedExpenseListModel
from src.app.qml_variant import coerce_mapping
from src.app.viewmodels.error_support import ErrorSupport
from src.app.workers.receipt_ocr_worker import ReceiptOcrWorker
from src.data.repositories.expense_dictionary_repo import (
    SqliteExpenseCategoryRepository,
    SqliteExpenseNameRepository,
    SqliteExpensePlaceRepository,
)
from src.data.repositories.recorded_expense_repo import (
    RecordedExpenseListFilters,
    SqliteRecordedExpenseRepository,
)
from src.domain.receipt_field_parser import ReceiptFieldParser
from src.domain.receipt_ocr import ReceiptOcrProvider
from src.domain.recorded_expenses import (
    ExpenseCategory,
    ExpenseName,
    ExpensePlace,
    RecordedExpenseCreate,
    RecordedExpenseService,
)
from src.integrations.receipt_ocr import create_receipt_ocr_provider, receipt_ocr_is_available

_DEFAULT_LIST_LIMIT = 200
_DEFAULT_SEARCH_LIMIT = 12
_SEARCH_DEBOUNCE_MS = 300


def _to_label_suggestions(
    items: Sequence[ExpenseName | ExpenseCategory | ExpensePlace],
) -> list[LabelSuggestion]:
    return [LabelSuggestion(id=item.id, label=item.label) for item in items]


def _parse_iso_date(value: str, *, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        msg = f"Invalid {field_name}: {value!r}"
        raise ValueError(msg) from exc


class RecordedExpensesViewModel(QObject):
    """Exposes recorded expense CRUD and dictionary autocomplete to QML."""

    expensesChanged = Signal()
    expenseCreated = Signal(str)
    expenseUpdated = Signal(str)
    expenseDeleted = Signal(str)
    errorChanged = Signal()
    searchTextChanged = Signal()
    filterDateRangeChanged = Signal()
    filtersChanged = Signal()
    isOcrRunningChanged = Signal()
    receiptOcrChanged = Signal()

    def __init__(
        self,
        service: RecordedExpenseService,
        expense_repo: SqliteRecordedExpenseRepository,
        name_repo: SqliteExpenseNameRepository,
        category_repo: SqliteExpenseCategoryRepository,
        place_repo: SqliteExpensePlaceRepository,
        *,
        list_limit: int = _DEFAULT_LIST_LIMIT,
        search_limit: int = _DEFAULT_SEARCH_LIMIT,
        ocr_provider: ReceiptOcrProvider | None = None,
        field_parser: ReceiptFieldParser | None = None,
        ocr_available: bool | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._expense_repo = expense_repo
        self._name_repo = name_repo
        self._category_repo = category_repo
        self._place_repo = place_repo
        self._list_limit = list_limit
        self._search_limit = search_limit
        self._ocr_provider = (
            ocr_provider if ocr_provider is not None else create_receipt_ocr_provider()
        )
        self._field_parser = field_parser if field_parser is not None else ReceiptFieldParser()
        self._ocr_available = receipt_ocr_is_available() if ocr_available is None else ocr_available
        self._ocr_worker: ReceiptOcrWorker | None = None
        self._is_ocr_running = False
        self._pending_receipt_path = ""
        self._suggested_amount = ""
        self._suggested_occurred_on = ""
        self._suggested_merchant = ""
        self._amount_is_low_confidence = False
        self._date_is_low_confidence = False
        self._merchant_is_low_confidence = False
        self._has_receipt_suggestions = False
        self._list_model = RecordedExpenseListModel(parent=self)
        self._name_suggestions = LabelSuggestionModel(parent=self)
        self._category_suggestions = LabelSuggestionModel(parent=self)
        self._place_suggestions = LabelSuggestionModel(parent=self)
        self._errors = ErrorSupport(self)
        self._pending_name_prefix = ""
        self._pending_category_prefix = ""
        self._pending_place_prefix = ""
        self._pending_list_search_text = ""
        self._search_text = ""
        self._search: str | None = None
        self._start_date: date | None = None
        self._end_date: date | None = None
        self._name_search_timer = self._create_search_timer(self._run_name_search)
        self._category_search_timer = self._create_search_timer(self._run_category_search)
        self._place_search_timer = self._create_search_timer(self._run_place_search)
        self._list_search_timer = self._create_search_timer(self._run_list_search)
        today = date.today()
        self._start_date = today.replace(day=1)
        self._end_date = today
        self._reload_list()

    @Property(QObject, constant=True)
    def expenseListModel(self) -> RecordedExpenseListModel:
        return self._list_model

    @Property(QObject, constant=True)
    def nameSuggestionModel(self) -> LabelSuggestionModel:
        return self._name_suggestions

    @Property(QObject, constant=True)
    def categorySuggestionModel(self) -> LabelSuggestionModel:
        return self._category_suggestions

    @Property(QObject, constant=True)
    def placeSuggestionModel(self) -> LabelSuggestionModel:
        return self._place_suggestions

    @Property(str, notify=errorChanged)
    def error(self) -> str:
        return self._errors.message

    @Property(str, notify=searchTextChanged)
    def searchText(self) -> str:
        return self._search_text

    @Property(str, notify=filterDateRangeChanged)
    def filterStartDate(self) -> str:
        return self._start_date.isoformat() if self._start_date is not None else ""

    @Property(str, notify=filterDateRangeChanged)
    def filterEndDate(self) -> str:
        return self._end_date.isoformat() if self._end_date is not None else ""

    @Property(bool, notify=filtersChanged)
    def hasActiveFilters(self) -> bool:
        return self._has_list_filters()

    @Property(bool, constant=True)
    def receiptOcrAvailable(self) -> bool:
        return self._ocr_available

    @Property(bool, notify=isOcrRunningChanged)
    def isOcrRunning(self) -> bool:
        return self._is_ocr_running

    @Property(str, notify=receiptOcrChanged)
    def pendingReceiptPath(self) -> str:
        return self._pending_receipt_path

    @Property(str, notify=receiptOcrChanged)
    def suggestedAmount(self) -> str:
        return self._suggested_amount

    @Property(str, notify=receiptOcrChanged)
    def suggestedOccurredOn(self) -> str:
        return self._suggested_occurred_on

    @Property(str, notify=receiptOcrChanged)
    def suggestedMerchant(self) -> str:
        return self._suggested_merchant

    @Property(bool, notify=receiptOcrChanged)
    def amountIsLowConfidence(self) -> bool:
        return self._amount_is_low_confidence

    @Property(bool, notify=receiptOcrChanged)
    def dateIsLowConfidence(self) -> bool:
        return self._date_is_low_confidence

    @Property(bool, notify=receiptOcrChanged)
    def merchantIsLowConfidence(self) -> bool:
        return self._merchant_is_low_confidence

    @Property(bool, notify=receiptOcrChanged)
    def hasReceiptSuggestions(self) -> bool:
        return self._has_receipt_suggestions

    @Slot()
    @Slot(int)
    def loadExpenses(self, limit: int = _DEFAULT_LIST_LIMIT) -> None:
        try:
            self._clear_error()
            self._list_limit = limit
            if self._has_list_filters():
                self._reload_list()
                return
            items = list(self._expense_repo.list_recent(limit))
            self._list_model.reset(items)
            self.expensesChanged.emit()
        except Exception as exc:
            self._set_error(exc)

    @Slot(str)
    def applyDatePreset(self, preset: str) -> None:
        try:
            self._clear_error()
            today = date.today()
            normalized = preset.strip().lower()
            if normalized == "this_month":
                start, end = today.replace(day=1), today
            elif normalized in {"last_30_days", "last_30"}:
                start, end = today - timedelta(days=29), today
            elif normalized == "ytd":
                start, end = today.replace(month=1, day=1), today
            else:
                msg = f"Unknown date preset: {preset!r}"
                raise ValueError(msg)
            self._start_date = start
            self._end_date = end
            self.filterDateRangeChanged.emit()
            self.filtersChanged.emit()
            self._reload_list()
        except Exception as exc:
            self._set_error(exc)

    @Slot(str, str)
    def setFilterDateRange(self, start_iso: str, end_iso: str) -> None:
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
            self.filterDateRangeChanged.emit()
            self.filtersChanged.emit()
            self._reload_list()
        except Exception as exc:
            self._set_error(exc)

    @Slot(str)
    def setSearchText(self, text: str) -> None:
        self._pending_list_search_text = text
        if text != self._search_text:
            self._search_text = text
            self.searchTextChanged.emit()
        self._list_search_timer.start()

    @Slot()
    def clearFilters(self) -> None:
        try:
            self._clear_error()
            self._search = None
            self._start_date = None
            self._end_date = None
            self._pending_list_search_text = ""
            if self._search_text != "":
                self._search_text = ""
                self.searchTextChanged.emit()
            self.filterDateRangeChanged.emit()
            self.filtersChanged.emit()
            self._reload_list()
        except Exception as exc:
            self._set_error(exc)

    @Slot("QVariant")
    def createExpense(self, dto: object) -> None:
        try:
            self._clear_error()
            create_dto = RecordedExpenseCreate.model_validate(
                coerce_mapping(dto, label="Recorded expense create data")
            )
            created = self._service.create(create_dto)
            pending_path = self._pending_receipt_path
            if pending_path:
                try:
                    self._service.attach_receipt_image(created.id, Path(pending_path))
                except Exception as attach_exc:
                    self._clear_receipt_ocr_state()
                    self._reload_list()
                    self.expenseCreated.emit(created.id)
                    self._set_error(attach_exc)
                    return
            self._clear_receipt_ocr_state()
            self._reload_list()
            self.expenseCreated.emit(created.id)
        except Exception as exc:
            self._set_error(exc)

    @Slot(str)
    def startReceiptOcr(self, image_path: str) -> None:
        try:
            self._clear_error()
            if self._is_ocr_running:
                return
            path = Path(image_path).expanduser()
            if not path.is_file():
                msg = f"Receipt image not found: {path}"
                raise ValueError(msg)
            self._pending_receipt_path = str(path.resolve())
            self._reset_suggestions()
            self._is_ocr_running = True
            self.isOcrRunningChanged.emit()
            self.receiptOcrChanged.emit()
            worker = ReceiptOcrWorker(self._ocr_provider, self._field_parser, path)
            worker.signals.finished.connect(self._on_ocr_finished)
            worker.signals.error.connect(self._on_ocr_error)
            self._ocr_worker = worker
            QThreadPool.globalInstance().start(worker)
        except Exception as exc:
            self._is_ocr_running = False
            self.isOcrRunningChanged.emit()
            self._set_error(exc)

    @Slot()
    def clearReceiptOcr(self) -> None:
        try:
            self._clear_error()
            self._clear_receipt_ocr_state()
        except Exception as exc:
            self._set_error(exc)

    @Slot(str, "QVariant")
    def updateExpense(self, expense_id: str, dto: object) -> None:
        try:
            self._clear_error()
            update_dto = RecordedExpenseCreate.model_validate(
                coerce_mapping(dto, label="Recorded expense update data")
            )
            self._service.update(expense_id, update_dto)
            self._reload_list()
            self.expenseUpdated.emit(expense_id)
        except Exception as exc:
            self._set_error(exc)

    @Slot(str)
    def deleteExpense(self, expense_id: str) -> None:
        try:
            self._clear_error()
            self._service.delete(expense_id)
            self._reload_list()
            self.expenseDeleted.emit(expense_id)
        except Exception as exc:
            self._set_error(exc)

    @Slot(str)
    def searchExpenseNames(self, prefix: str) -> None:
        self._pending_name_prefix = prefix
        self._name_search_timer.start()

    @Slot(str)
    def searchCategories(self, prefix: str) -> None:
        self._pending_category_prefix = prefix
        self._category_search_timer.start()

    @Slot(str)
    def searchPlaces(self, prefix: str) -> None:
        self._pending_place_prefix = prefix
        self._place_search_timer.start()

    @Slot()
    def clearError(self) -> None:
        self._clear_error()

    @Slot()
    def retranslate(self) -> None:
        self._errors.retranslate()

    def _create_search_timer(self, handler: Callable[[], None]) -> QTimer:
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.setInterval(_SEARCH_DEBOUNCE_MS)
        timer.timeout.connect(handler)
        return timer

    def _run_name_search(self) -> None:
        self._run_label_search(
            self._pending_name_prefix,
            self._name_repo.search,
            self._name_suggestions,
        )

    def _run_category_search(self) -> None:
        self._run_label_search(
            self._pending_category_prefix,
            self._category_repo.search,
            self._category_suggestions,
        )

    def _run_place_search(self) -> None:
        self._run_label_search(
            self._pending_place_prefix,
            self._place_repo.search,
            self._place_suggestions,
        )

    def _run_list_search(self) -> None:
        try:
            self._clear_error()
            stripped = self._pending_list_search_text.strip()
            self._search = stripped if stripped else None
            self.filtersChanged.emit()
            self._reload_list()
        except Exception as exc:
            self._set_error(exc)

    def _run_label_search(
        self,
        prefix: str,
        search_fn: Callable[[str, int], Sequence[ExpenseName | ExpenseCategory | ExpensePlace]],
        model: LabelSuggestionModel,
    ) -> None:
        try:
            self._clear_error()
            results = search_fn(prefix, self._search_limit)
            model.reset(_to_label_suggestions(list(results)))
        except Exception as exc:
            self._set_error(exc)

    def _has_list_filters(self) -> bool:
        return (
            self._search is not None or self._start_date is not None or self._end_date is not None
        )

    def _reload_list(self) -> None:
        if self._has_list_filters():
            items = list(
                self._expense_repo.list_filtered(
                    RecordedExpenseListFilters(
                        start_date=self._start_date,
                        end_date=self._end_date,
                        search=self._search,
                        limit=self._list_limit,
                    )
                )
            )
        else:
            items = list(self._expense_repo.list_recent(self._list_limit))
        self._list_model.reset(items)
        self.expensesChanged.emit()

    def _on_ocr_finished(self, payload: object) -> None:
        if not self._is_ocr_running:
            return
        self._ocr_worker = None
        self._is_ocr_running = False
        fields = _ocr_fields(payload)
        self._suggested_amount = _format_suggested_amount(fields.get("amount"))
        occurred_on = fields.get("occurred_on")
        self._suggested_occurred_on = occurred_on if isinstance(occurred_on, str) else ""
        merchant = fields.get("merchant")
        self._suggested_merchant = merchant.strip() if isinstance(merchant, str) else ""
        self._amount_is_low_confidence = bool(fields.get("amount_is_low_confidence", True))
        self._date_is_low_confidence = bool(fields.get("date_is_low_confidence", True))
        self._merchant_is_low_confidence = bool(fields.get("merchant_is_low_confidence", True))
        self._has_receipt_suggestions = True
        self.isOcrRunningChanged.emit()
        self.receiptOcrChanged.emit()

    def _on_ocr_error(self, message: str) -> None:
        if not self._is_ocr_running:
            return
        self._ocr_worker = None
        self._is_ocr_running = False
        self._reset_suggestions()
        self.isOcrRunningChanged.emit()
        self.receiptOcrChanged.emit()
        self._set_error(message)

    def _clear_receipt_ocr_state(self) -> None:
        was_running = self._is_ocr_running
        had_state = (
            was_running
            or self._pending_receipt_path != ""
            or self._has_receipt_suggestions
            or self._ocr_worker is not None
        )
        self._ocr_worker = None
        self._is_ocr_running = False
        self._pending_receipt_path = ""
        self._reset_suggestions()
        if was_running:
            self.isOcrRunningChanged.emit()
        if had_state:
            self.receiptOcrChanged.emit()

    def _reset_suggestions(self) -> None:
        self._suggested_amount = ""
        self._suggested_occurred_on = ""
        self._suggested_merchant = ""
        self._amount_is_low_confidence = False
        self._date_is_low_confidence = False
        self._merchant_is_low_confidence = False
        self._has_receipt_suggestions = False

    def _set_error(self, exc: BaseException | str) -> None:
        if isinstance(exc, BaseException):
            self._errors.set_from_exception(exc)
            return
        self._errors.set(exc)

    def _clear_error(self) -> None:
        if not self._errors.clear():
            return
        self.errorChanged.emit()


def _ocr_fields(payload: object) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping):
        return {}
    fields = payload.get("fields")
    if not isinstance(fields, Mapping):
        return {}
    return fields


def _format_suggested_amount(value: object) -> str:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return ""
    return f"{float(value):.2f}"
