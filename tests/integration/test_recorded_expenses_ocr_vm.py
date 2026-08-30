from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from sqlalchemy.engine import Connection

from src.app.viewmodels.recorded_expenses_view_model import RecordedExpensesViewModel
from src.data.repositories.expense_dictionary_repo import (
    SqliteExpenseCategoryRepository,
    SqliteExpenseNameRepository,
    SqliteExpensePlaceRepository,
)
from src.data.repositories.recorded_expense_repo import SqliteRecordedExpenseRepository
from src.domain.exceptions import ReceiptOcrUnavailableError
from src.domain.receipt_field_parser import ReceiptFieldParser
from src.domain.receipt_image_store import ReceiptImageStore
from src.domain.receipt_ocr import ReceiptOcrLine, ReceiptOcrResult
from src.domain.recorded_expenses import RecordedExpenseService


class _FakeOcrProvider:
    def __init__(
        self,
        *,
        lines: tuple[tuple[str, float], ...] = (),
        error: Exception | None = None,
    ) -> None:
        self._lines = lines
        self._error = error

    @property
    def provider_id(self) -> str:
        return "fake"

    def extract_text(self, image_path: Path) -> ReceiptOcrResult:
        _ = image_path
        if self._error is not None:
            raise self._error
        ocr_lines = tuple(
            ReceiptOcrLine(text=text, confidence=confidence) for text, confidence in self._lines
        )
        overall = sum(line.confidence for line in ocr_lines) / len(ocr_lines) if ocr_lines else 0.0
        return ReceiptOcrResult(
            lines=ocr_lines,
            provider_id=self.provider_id,
            overall_confidence=overall,
        )


def _make_vm(
    recorded_expense_repository: SqliteRecordedExpenseRepository,
    expense_name_repository: SqliteExpenseNameRepository,
    expense_category_repository: SqliteExpenseCategoryRepository,
    expense_place_repository: SqliteExpensePlaceRepository,
    *,
    tmp_path: Path,
    provider: _FakeOcrProvider,
) -> tuple[RecordedExpensesViewModel, Path, ReceiptImageStore]:
    store = ReceiptImageStore(tmp_path / "appdata")
    service = RecordedExpenseService(
        recorded_expense_repository,
        expense_name_repository,
        expense_category_repository,
        expense_place_repository,
        receipt_image_store=store,
    )
    image = tmp_path / "receipt.jpg"
    image.write_bytes(b"fake-bytes")
    vm = RecordedExpensesViewModel(
        service,
        recorded_expense_repository,
        expense_name_repository,
        expense_category_repository,
        expense_place_repository,
        ocr_provider=provider,
        field_parser=ReceiptFieldParser(reference_date=date(2026, 8, 29)),
        ocr_available=True,
    )
    return vm, image, store


@pytest.mark.integration
def test_start_receipt_ocr_fills_suggestions(
    qtbot: object,
    tmp_path: Path,
    recorded_expense_repository: SqliteRecordedExpenseRepository,
    expense_name_repository: SqliteExpenseNameRepository,
    expense_category_repository: SqliteExpenseCategoryRepository,
    expense_place_repository: SqliteExpensePlaceRepository,
) -> None:
    vm, image, _store = _make_vm(
        recorded_expense_repository,
        expense_name_repository,
        expense_category_repository,
        expense_place_repository,
        tmp_path=tmp_path,
        provider=_FakeOcrProvider(
            lines=(("Cafe Nero", 1.0), ("Date: 2026-01-15", 1.0), ("TOTAL 12.50", 1.0)),
        ),
    )

    vm.startReceiptOcr(str(image))
    qtbot.waitUntil(lambda: vm.isOcrRunning is False, timeout=5000)  # type: ignore[attr-defined]

    assert vm.error == ""
    assert vm.pendingReceiptPath == str(image.resolve())
    assert vm.suggestedAmount == "12.50"
    assert vm.suggestedOccurredOn == "2026-01-15"
    assert vm.suggestedMerchant == "Cafe Nero"
    assert vm.hasReceiptSuggestions is True
    assert vm.amountIsLowConfidence is False
    assert vm.dateIsLowConfidence is False


@pytest.mark.integration
def test_start_receipt_ocr_flags_low_confidence_fields(
    qtbot: object,
    tmp_path: Path,
    recorded_expense_repository: SqliteRecordedExpenseRepository,
    expense_name_repository: SqliteExpenseNameRepository,
    expense_category_repository: SqliteExpenseCategoryRepository,
    expense_place_repository: SqliteExpensePlaceRepository,
) -> None:
    vm, image, _store = _make_vm(
        recorded_expense_repository,
        expense_name_repository,
        expense_category_repository,
        expense_place_repository,
        tmp_path=tmp_path,
        provider=_FakeOcrProvider(lines=(("Corner Shop", 0.4), ("12.50", 0.5))),
    )

    vm.startReceiptOcr(str(image))
    qtbot.waitUntil(lambda: vm.isOcrRunning is False, timeout=5000)  # type: ignore[attr-defined]

    assert vm.error == ""
    assert vm.hasReceiptSuggestions is True
    assert vm.amountIsLowConfidence is True
    assert vm.dateIsLowConfidence is True
    assert vm.merchantIsLowConfidence is True


@pytest.mark.integration
def test_create_expense_attaches_pending_receipt(
    qtbot: object,
    tmp_path: Path,
    db_conn: Connection,
    recorded_expense_repository: SqliteRecordedExpenseRepository,
    expense_name_repository: SqliteExpenseNameRepository,
    expense_category_repository: SqliteExpenseCategoryRepository,
    expense_place_repository: SqliteExpensePlaceRepository,
) -> None:
    vm, image, store = _make_vm(
        recorded_expense_repository,
        expense_name_repository,
        expense_category_repository,
        expense_place_repository,
        tmp_path=tmp_path,
        provider=_FakeOcrProvider(
            lines=(("Cafe Nero", 1.0), ("TOTAL 12.50", 1.0)),
        ),
    )

    vm.startReceiptOcr(str(image))
    qtbot.waitUntil(lambda: vm.isOcrRunning is False, timeout=5000)  # type: ignore[attr-defined]
    created_ids: list[str] = []
    vm.expenseCreated.connect(created_ids.append)
    vm.createExpense(
        {
            "amount": 12.5,
            "currency": "USD",
            "name": "Cafe Nero",
            "occurred_on": "2026-01-15",
        }
    )
    db_conn.commit()

    assert vm.error == ""
    assert vm.pendingReceiptPath == ""
    assert created_ids
    expense_id = created_ids[0]
    stored = recorded_expense_repository.find_by_id(expense_id)
    assert stored is not None
    assert stored.receipt_image_path is not None
    assert store.resolve_path(stored.receipt_image_path).is_file()


@pytest.mark.integration
def test_ocr_error_keeps_manual_entry_and_pending_image(
    qtbot: object,
    tmp_path: Path,
    db_conn: Connection,
    recorded_expense_repository: SqliteRecordedExpenseRepository,
    expense_name_repository: SqliteExpenseNameRepository,
    expense_category_repository: SqliteExpenseCategoryRepository,
    expense_place_repository: SqliteExpensePlaceRepository,
) -> None:
    vm, image, store = _make_vm(
        recorded_expense_repository,
        expense_name_repository,
        expense_category_repository,
        expense_place_repository,
        tmp_path=tmp_path,
        provider=_FakeOcrProvider(
            error=ReceiptOcrUnavailableError(
                "Receipt scanning is not available on this platform (linux). "
                "Enter the expense manually."
            ),
        ),
    )

    vm.startReceiptOcr(str(image))
    qtbot.waitUntil(lambda: vm.isOcrRunning is False, timeout=5000)  # type: ignore[attr-defined]

    assert "linux" in vm.error
    assert vm.hasReceiptSuggestions is False
    assert vm.pendingReceiptPath == str(image.resolve())

    vm.clearError()
    vm.createExpense(
        {
            "amount": 9.0,
            "currency": "USD",
            "name": "Manual",
        }
    )
    db_conn.commit()

    assert vm.error == ""
    expense_id = vm.expenseListModel.data(
        vm.expenseListModel.index(0, 0),
        vm.expenseListModel.EXPENSE_ID_ROLE,
    )
    assert isinstance(expense_id, str)
    stored = recorded_expense_repository.find_by_id(expense_id)
    assert stored is not None
    assert stored.receipt_image_path is not None
    assert store.resolve_path(stored.receipt_image_path).is_file()


@pytest.mark.integration
def test_clear_receipt_ocr_drops_pending_image(
    qtbot: object,
    tmp_path: Path,
    db_conn: Connection,
    recorded_expense_repository: SqliteRecordedExpenseRepository,
    expense_name_repository: SqliteExpenseNameRepository,
    expense_category_repository: SqliteExpenseCategoryRepository,
    expense_place_repository: SqliteExpensePlaceRepository,
) -> None:
    vm, image, _store = _make_vm(
        recorded_expense_repository,
        expense_name_repository,
        expense_category_repository,
        expense_place_repository,
        tmp_path=tmp_path,
        provider=_FakeOcrProvider(lines=(("TOTAL 12.50", 1.0),)),
    )

    vm.startReceiptOcr(str(image))
    qtbot.waitUntil(lambda: vm.isOcrRunning is False, timeout=5000)  # type: ignore[attr-defined]
    vm.clearReceiptOcr()

    assert vm.pendingReceiptPath == ""
    assert vm.hasReceiptSuggestions is False
    assert vm.suggestedAmount == ""

    vm.createExpense(
        {
            "amount": 12.5,
            "currency": "USD",
            "name": "Manual",
        }
    )
    db_conn.commit()

    expense_id = vm.expenseListModel.data(
        vm.expenseListModel.index(0, 0),
        vm.expenseListModel.EXPENSE_ID_ROLE,
    )
    assert isinstance(expense_id, str)
    stored = recorded_expense_repository.find_by_id(expense_id)
    assert stored is not None
    assert stored.receipt_image_path is None


@pytest.mark.integration
def test_missing_receipt_image_sets_error(
    recorded_expense_repository: SqliteRecordedExpenseRepository,
    expense_name_repository: SqliteExpenseNameRepository,
    expense_category_repository: SqliteExpenseCategoryRepository,
    expense_place_repository: SqliteExpensePlaceRepository,
    tmp_path: Path,
) -> None:
    vm, _image, _store = _make_vm(
        recorded_expense_repository,
        expense_name_repository,
        expense_category_repository,
        expense_place_repository,
        tmp_path=tmp_path,
        provider=_FakeOcrProvider(),
    )

    vm.startReceiptOcr(str(tmp_path / "missing.jpg"))

    assert vm.isOcrRunning is False
    assert vm.error != ""
    assert "not found" in vm.error.lower()


@pytest.mark.integration
def test_refresh_receipt_ocr_availability_updates_flag(
    recorded_expense_repository: SqliteRecordedExpenseRepository,
    expense_name_repository: SqliteExpenseNameRepository,
    expense_category_repository: SqliteExpenseCategoryRepository,
    expense_place_repository: SqliteExpensePlaceRepository,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _FakeOcrProvider()
    vm, _image, _store = _make_vm(
        recorded_expense_repository,
        expense_name_repository,
        expense_category_repository,
        expense_place_repository,
        tmp_path=tmp_path,
        provider=provider,
    )
    vm._ocr_available = False  # noqa: SLF001
    monkeypatch.setattr(
        "src.app.viewmodels.recorded_expenses_view_model.receipt_ocr_is_available",
        lambda: True,
    )
    monkeypatch.setattr(
        "src.app.viewmodels.recorded_expenses_view_model.create_receipt_ocr_provider",
        lambda: provider,
    )

    vm.refreshReceiptOcrAvailability()

    assert vm.receiptOcrAvailable is True
