from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.domain.exceptions import RecordedExpenseValidationError
from src.domain.recorded_expenses import (
    ExpenseCategory,
    ExpenseName,
    ExpensePlace,
    RecordedExpense,
    RecordedExpenseCreate,
    RecordedExpensePersistDto,
    RecordedExpenseService,
    normalize_dictionary_label,
)


class FakeNameRepository:
    def __init__(self) -> None:
        self._by_normalized: dict[str, ExpenseName] = {}

    def get_or_create(self, label: str) -> ExpenseName:
        key = normalize_dictionary_label(label)
        existing = self._by_normalized.get(key)
        if existing is not None:
            return existing
        created = ExpenseName(id=str(uuid4()), label=label.strip())
        self._by_normalized[key] = created
        return created

    def search(self, prefix: str, limit: int) -> Sequence[ExpenseName]:
        _ = prefix, limit
        return []


class FakeCategoryRepository:
    def __init__(self) -> None:
        self._by_normalized: dict[str, ExpenseCategory] = {}

    def get_or_create(self, label: str) -> ExpenseCategory:
        key = normalize_dictionary_label(label)
        existing = self._by_normalized.get(key)
        if existing is not None:
            return existing
        created = ExpenseCategory(id=str(uuid4()), label=label.strip())
        self._by_normalized[key] = created
        return created

    def search(self, prefix: str, limit: int) -> Sequence[ExpenseCategory]:
        _ = prefix, limit
        return []


class FakePlaceRepository:
    def get_or_create(self, label: str) -> ExpensePlace:
        return ExpensePlace(id=str(uuid4()), label=label.strip())

    def search(self, prefix: str, limit: int) -> Sequence[ExpensePlace]:
        _ = prefix, limit
        return []


class FakeRecordedExpenseRepository:
    def __init__(self) -> None:
        self._expenses: dict[str, RecordedExpense] = {}

    def find_by_id(self, expense_id: str) -> RecordedExpense | None:
        return self._expenses.get(expense_id)

    def create(self, dto: RecordedExpensePersistDto) -> RecordedExpense:
        expense_id = str(uuid4())
        now = "2026-08-01T00:00:00+00:00"
        expense = RecordedExpense(
            id=expense_id,
            amount=dto.amount,
            currency=dto.currency,
            occurred_on=dto.occurred_on,
            name_id=dto.name_id,
            category_id=dto.category_id,
            place_id=dto.place_id,
            note=dto.note,
            created_at=now,
            updated_at=now,
        )
        self._expenses[expense_id] = expense
        return expense

    def update(self, expense_id: str, dto: RecordedExpensePersistDto) -> RecordedExpense:
        existing = self._expenses[expense_id]
        updated = existing.model_copy(
            update={
                "amount": dto.amount,
                "currency": dto.currency,
                "occurred_on": dto.occurred_on,
                "name_id": dto.name_id,
                "category_id": dto.category_id,
                "place_id": dto.place_id,
                "note": dto.note,
                "updated_at": "2026-08-01T01:00:00+00:00",
            }
        )
        self._expenses[expense_id] = updated
        return updated

    def delete(self, expense_id: str) -> None:
        self._expenses.pop(expense_id, None)


@pytest.fixture
def service() -> tuple[RecordedExpenseService, FakeNameRepository]:
    expense_repo = FakeRecordedExpenseRepository()
    name_repo = FakeNameRepository()
    service = RecordedExpenseService(
        expense_repo,
        name_repo,
        FakeCategoryRepository(),
        FakePlaceRepository(),
    )
    return service, name_repo


def test_normalize_dictionary_label_trims_and_lowercases() -> None:
    assert normalize_dictionary_label("  Netflix  ") == "netflix"


def test_create_reuses_same_name_id_for_different_casing(
    service: tuple[RecordedExpenseService, FakeNameRepository],
) -> None:
    recorded_expense_service, name_repo = service

    first = recorded_expense_service.create(
        RecordedExpenseCreate(amount=10.0, currency="USD", name="Netflix")
    )
    second = recorded_expense_service.create(
        RecordedExpenseCreate(amount=15.0, currency="USD", name="  netflix ")
    )

    assert first.name_id == second.name_id
    assert len(name_repo._by_normalized) == 1


def test_create_defaults_occurred_on_to_today(
    service: tuple[RecordedExpenseService, FakeNameRepository],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from unittest.mock import MagicMock

    import src.domain.recorded_expenses as recorded_expenses_module

    recorded_expense_service, _ = service
    mock_date = MagicMock()
    mock_date.today.return_value = date(2026, 8, 1)
    monkeypatch.setattr(recorded_expenses_module, "date", mock_date)

    created = recorded_expense_service.create(
        RecordedExpenseCreate(amount=5.0, currency="EUR", name="Snack")
    )

    assert created.occurred_on == date(2026, 8, 1)


def test_create_normalizes_currency(
    service: tuple[RecordedExpenseService, FakeNameRepository],
) -> None:
    recorded_expense_service, _ = service

    created = recorded_expense_service.create(
        RecordedExpenseCreate(amount=5.0, currency=" eur ", name="Snack")
    )

    assert created.currency == "EUR"


@pytest.mark.parametrize(
    ("amount", "match"),
    [
        (0.0, "Amount must be greater than zero"),
        (-1.0, "Amount must be greater than zero"),
    ],
)
def test_create_rejects_non_positive_amount(amount: float, match: str) -> None:
    with pytest.raises(ValidationError, match=match):
        RecordedExpenseCreate(amount=amount, currency="USD", name="Coffee")


@pytest.mark.parametrize(
    ("currency", "match"),
    [
        ("", "Currency is required"),
        ("   ", "Currency is required"),
    ],
)
def test_create_rejects_empty_currency(currency: str, match: str) -> None:
    with pytest.raises(ValidationError, match=match):
        RecordedExpenseCreate(amount=1.0, currency=currency, name="Coffee")


def test_create_rejects_empty_name() -> None:
    with pytest.raises(ValidationError, match="Name is required"):
        RecordedExpenseCreate(amount=1.0, currency="USD", name="   ")


def test_update_raises_when_expense_not_found(
    service: tuple[RecordedExpenseService, FakeNameRepository],
) -> None:
    recorded_expense_service, _ = service

    with pytest.raises(RecordedExpenseValidationError, match="not found"):
        recorded_expense_service.update(
            "missing-id",
            RecordedExpenseCreate(amount=1.0, currency="USD", name="Coffee"),
        )


def test_delete_raises_when_expense_not_found(
    service: tuple[RecordedExpenseService, FakeNameRepository],
) -> None:
    recorded_expense_service, _ = service

    with pytest.raises(RecordedExpenseValidationError, match="not found"):
        recorded_expense_service.delete("missing-id")
