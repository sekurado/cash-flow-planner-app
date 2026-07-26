from __future__ import annotations

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtQml import QQmlApplicationEngine

from src.app.viewmodels.entries_vm import EntriesViewModel
from src.data.repositories.plan_repo import PlanCreateDto, SqlitePlanRepository
from src.domain.entities import EntryType


@pytest.fixture
def sample_plan(plan_repository: SqlitePlanRepository) -> str:
    plan = plan_repository.create(
        PlanCreateDto(name="Test Plan", base_currency="USD", initial_balance=1000.0)
    )
    return plan.id


@pytest.mark.integration
def test_create_entry_increases_row_count(
    qt_app: object,
    sample_plan: str,
    entry_repository: object,
) -> None:
    vm = EntriesViewModel(entry_repository)
    assert vm.entryListModel.rowCount() == 0

    vm.createEntry(
        {
            "plan_id": sample_plan,
            "entry_type": EntryType.INCOME.value,
            "name": "Salary",
            "date_pattern": "10..",
            "amount": 500.0,
            "currency": "USD",
        }
    )

    assert vm.error == ""
    assert vm.entryListModel.rowCount() == 1


@pytest.mark.integration
def test_describe_pattern_valid(entry_repository: object, qt_app: object) -> None:
    QSettings().setValue("language", "en")
    vm = EntriesViewModel(entry_repository)
    assert vm.describePattern("10..") == "Monthly on the 10th"


@pytest.mark.integration
def test_describe_pattern_invalid(entry_repository: object, qt_app: object) -> None:
    vm = EntriesViewModel(entry_repository)
    assert vm.describePattern("not-valid") == ""


@pytest.mark.integration
def test_delete_entry_clears_row_count(
    qt_app: object,
    sample_plan: str,
    entry_repository: object,
) -> None:
    vm = EntriesViewModel(entry_repository)
    vm.createEntry(
        {
            "plan_id": sample_plan,
            "entry_type": EntryType.INCOME.value,
            "name": "Salary",
            "date_pattern": "10..",
            "amount": 500.0,
            "currency": "USD",
        }
    )
    entry_id = vm.entries[0]["id"]
    assert vm.entryListModel.rowCount() == 1

    vm.deleteEntry(entry_id)

    assert vm.error == ""
    assert vm.entryListModel.rowCount() == 0
    assert entry_repository.find_by_plan_id(sample_plan) == []


@pytest.mark.integration
def test_describe_pattern_returns_non_empty_string(
    entry_repository: object,
    qt_app: object,
) -> None:
    vm = EntriesViewModel(entry_repository)
    description = vm.describePattern("10..")
    assert description != ""


@pytest.mark.integration
def test_duplicate_entry_names_allowed(
    qt_app: object,
    sample_plan: str,
    entry_repository: object,
) -> None:
    vm = EntriesViewModel(entry_repository)
    dto = {
        "plan_id": sample_plan,
        "entry_type": EntryType.INCOME.value,
        "name": "Salary",
        "date_pattern": "10..",
        "amount": 500.0,
        "currency": "USD",
    }
    vm.createEntry(dto)
    vm.createEntry({**dto, "amount": 600.0})

    assert vm.error == ""
    assert vm.entryListModel.rowCount() == 2
    assert len(entry_repository.find_by_plan_id(sample_plan)) == 2


@pytest.mark.integration
def test_create_entry_invalid_dto_sets_error(
    qt_app: object,
    sample_plan: str,
    entry_repository: object,
) -> None:
    vm = EntriesViewModel(entry_repository)

    vm.createEntry(
        {
            "plan_id": sample_plan,
            "entry_type": "invalid",
            "name": "Salary",
            "date_pattern": "10..",
            "amount": 500.0,
            "currency": "USD",
        }
    )

    assert vm.error != ""
    assert vm.entryListModel.rowCount() == 0
    assert entry_repository.find_by_plan_id(sample_plan) == []


@pytest.mark.integration
def test_create_entry_accepts_qjsvalue_from_qml(
    qt_app: object,
    sample_plan: str,
    entry_repository: object,
) -> None:
    vm = EntriesViewModel(entry_repository)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("entriesViewModel", vm)

    qml = f"""
    import QtQuick
    Item {{
        Component.onCompleted: {{
            entriesViewModel.createEntry({{
                plan_id: "{sample_plan}",
                entry_type: "income",
                name: "Salary",
                date_pattern: "10..",
                amount: 500,
                currency: "USD",
                category: null
            }})
        }}
    }}
    """
    engine.loadData(qml.encode())
    assert engine.rootObjects()
    qt_app.processEvents()  # type: ignore[attr-defined]

    assert vm.error == ""
    assert vm.entryListModel.rowCount() == 1
