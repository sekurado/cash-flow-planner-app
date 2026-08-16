from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, ConfigDict, field_validator

from src.domain.exceptions import RecordedExpenseValidationError
from src.domain.receipt_image_store import ReceiptImageStore


class ExpenseName(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    label: str


class ExpenseCategory(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    label: str


class ExpensePlace(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    label: str


class RecordedExpense(BaseModel):
    id: str
    amount: float
    currency: str
    occurred_on: date
    name_id: str
    category_id: str | None = None
    place_id: str | None = None
    note: str | None = None
    receipt_image_path: str | None = None
    created_at: str
    updated_at: str


class RecordedExpenseCreate(BaseModel):
    amount: float
    currency: str
    name: str
    category: str | None = None
    place: str | None = None
    occurred_on: date | None = None
    note: str | None = None

    @field_validator("amount")
    @classmethod
    def _positive_amount(cls, value: float) -> float:
        if value <= 0:
            msg = "Amount must be greater than zero"
            raise ValueError(msg)
        return value

    @field_validator("currency")
    @classmethod
    def _normalize_currency(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            msg = "Currency is required"
            raise ValueError(msg)
        return stripped.upper()

    @field_validator("name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            msg = "Name is required"
            raise ValueError(msg)
        return stripped

    @field_validator("category", "place", "note", mode="before")
    @classmethod
    def _empty_optional_to_none(cls, value: object) -> object | None:
        if value is None:
            return None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped if stripped else None
        return value


class RecordedExpensePersistDto(BaseModel):
    amount: float
    currency: str
    occurred_on: date
    name_id: str
    category_id: str | None = None
    place_id: str | None = None
    note: str | None = None
    receipt_image_path: str | None = None


class AbstractExpenseNameRepository(Protocol):
    def get_or_create(self, label: str) -> ExpenseName: ...

    def search(self, prefix: str, limit: int) -> Sequence[ExpenseName]: ...


class AbstractExpenseCategoryRepository(Protocol):
    def get_or_create(self, label: str) -> ExpenseCategory: ...

    def search(self, prefix: str, limit: int) -> Sequence[ExpenseCategory]: ...


class AbstractExpensePlaceRepository(Protocol):
    def get_or_create(self, label: str) -> ExpensePlace: ...

    def search(self, prefix: str, limit: int) -> Sequence[ExpensePlace]: ...


class AbstractRecordedExpenseRepository(Protocol):
    def find_by_id(self, expense_id: str) -> RecordedExpense | None: ...

    def create(self, dto: RecordedExpensePersistDto) -> RecordedExpense: ...

    def update(self, expense_id: str, dto: RecordedExpensePersistDto) -> RecordedExpense: ...

    def update_receipt_image_path(
        self,
        expense_id: str,
        receipt_image_path: str | None,
    ) -> RecordedExpense: ...

    def delete(self, expense_id: str) -> None: ...


def normalize_dictionary_label(label: str) -> str:
    """Return the deduplication key for dictionary labels (trim + lower-case)."""
    return label.strip().lower()


class RecordedExpenseService:
    def __init__(
        self,
        expense_repo: AbstractRecordedExpenseRepository,
        name_repo: AbstractExpenseNameRepository,
        category_repo: AbstractExpenseCategoryRepository,
        place_repo: AbstractExpensePlaceRepository,
        *,
        receipt_image_store: ReceiptImageStore | None = None,
    ) -> None:
        self._expense_repo = expense_repo
        self._name_repo = name_repo
        self._category_repo = category_repo
        self._place_repo = place_repo
        self._receipt_image_store = receipt_image_store

    def create(self, data: RecordedExpenseCreate) -> RecordedExpense:
        persist_dto = self._resolve_persist_dto(data)
        return self._expense_repo.create(persist_dto)

    def update(self, expense_id: str, data: RecordedExpenseCreate) -> RecordedExpense:
        if self._expense_repo.find_by_id(expense_id) is None:
            msg = f"Recorded expense not found: {expense_id}"
            raise RecordedExpenseValidationError(msg)
        persist_dto = self._resolve_persist_dto(data)
        return self._expense_repo.update(expense_id, persist_dto)

    def delete(self, expense_id: str) -> None:
        expense = self._expense_repo.find_by_id(expense_id)
        if expense is None:
            msg = f"Recorded expense not found: {expense_id}"
            raise RecordedExpenseValidationError(msg)
        if self._receipt_image_store is not None:
            self._receipt_image_store.delete_receipt_image(expense.receipt_image_path)
        self._expense_repo.delete(expense_id)

    def attach_receipt_image(self, expense_id: str, source_image: Path) -> RecordedExpense:
        expense = self._expense_repo.find_by_id(expense_id)
        if expense is None:
            msg = f"Recorded expense not found: {expense_id}"
            raise RecordedExpenseValidationError(msg)
        if self._receipt_image_store is None:
            msg = "Receipt image storage is not configured"
            raise RecordedExpenseValidationError(msg)

        relative_path = self._receipt_image_store.save_receipt_image(expense_id, source_image)
        previous_path = expense.receipt_image_path
        try:
            updated = self._expense_repo.update_receipt_image_path(expense_id, relative_path)
        except Exception:
            self._receipt_image_store.delete_receipt_image(relative_path)
            raise
        if previous_path and previous_path != relative_path:
            self._receipt_image_store.delete_receipt_image(previous_path)
        return updated

    def _resolve_persist_dto(self, data: RecordedExpenseCreate) -> RecordedExpensePersistDto:
        name = self._name_repo.get_or_create(data.name)
        category_id = self._resolve_optional_label_id(data.category, self._category_repo)
        place_id = self._resolve_optional_label_id(data.place, self._place_repo)
        occurred_on = data.occurred_on if data.occurred_on is not None else date.today()
        return RecordedExpensePersistDto(
            amount=data.amount,
            currency=data.currency,
            occurred_on=occurred_on,
            name_id=name.id,
            category_id=category_id,
            place_id=place_id,
            note=data.note,
        )

    def _resolve_optional_label_id(
        self,
        label: str | None,
        repo: AbstractExpenseCategoryRepository | AbstractExpensePlaceRepository,
    ) -> str | None:
        if label is None:
            return None
        return repo.get_or_create(label).id
