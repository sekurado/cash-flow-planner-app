from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from src.app.models.label_suggestion_model import LabelSuggestion, LabelSuggestionModel
from src.app.models.recorded_expense_list_model import RecordedExpenseListModel
from src.app.qml_variant import coerce_mapping
from src.app.viewmodels.error_support import ErrorSupport
from src.data.repositories.expense_dictionary_repo import (
    SqliteExpenseCategoryRepository,
    SqliteExpenseNameRepository,
    SqliteExpensePlaceRepository,
)
from src.data.repositories.recorded_expense_repo import SqliteRecordedExpenseRepository
from src.domain.recorded_expenses import (
    ExpenseCategory,
    ExpenseName,
    ExpensePlace,
    RecordedExpenseCreate,
    RecordedExpenseService,
)

_DEFAULT_LIST_LIMIT = 200
_DEFAULT_SEARCH_LIMIT = 12
_SEARCH_DEBOUNCE_MS = 300


def _to_label_suggestions(
    items: Sequence[ExpenseName | ExpenseCategory | ExpensePlace],
) -> list[LabelSuggestion]:
    return [LabelSuggestion(id=item.id, label=item.label) for item in items]


class RecordedExpensesViewModel(QObject):
    """Exposes recorded expense CRUD and dictionary autocomplete to QML."""

    expensesChanged = Signal()
    expenseCreated = Signal(str)
    expenseUpdated = Signal(str)
    expenseDeleted = Signal(str)
    errorChanged = Signal()

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
        self._list_model = RecordedExpenseListModel(parent=self)
        self._name_suggestions = LabelSuggestionModel(parent=self)
        self._category_suggestions = LabelSuggestionModel(parent=self)
        self._place_suggestions = LabelSuggestionModel(parent=self)
        self._errors = ErrorSupport(self)
        self._pending_name_prefix = ""
        self._pending_category_prefix = ""
        self._pending_place_prefix = ""
        self._name_search_timer = self._create_search_timer(self._run_name_search)
        self._category_search_timer = self._create_search_timer(self._run_category_search)
        self._place_search_timer = self._create_search_timer(self._run_place_search)

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

    @Slot()
    @Slot(int)
    def loadExpenses(self, limit: int = _DEFAULT_LIST_LIMIT) -> None:
        try:
            self._clear_error()
            items = list(self._expense_repo.list_recent(limit))
            self._list_model.reset(items)
            self.expensesChanged.emit()
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
            self._reload_list()
            self.expenseCreated.emit(created.id)
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

    def _reload_list(self) -> None:
        items = list(self._expense_repo.list_recent(self._list_limit))
        self._list_model.reset(items)
        self.expensesChanged.emit()

    def _set_error(self, exc: BaseException | str) -> None:
        if isinstance(exc, BaseException):
            self._errors.set_from_exception(exc)
            return
        self._errors.set(exc)

    def _clear_error(self) -> None:
        if not self._errors.clear():
            return
        self.errorChanged.emit()
