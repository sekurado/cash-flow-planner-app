from __future__ import annotations

import csv
from pathlib import Path

import pytest

from src.app.viewmodels.entries_vm import EntriesViewModel
from src.app.viewmodels.import_vm import ImportViewModel
from src.data.repositories.plan_repo import PlanCreateDto, SqlitePlanRepository
from src.integrations.import_service import ImportService


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    headers = ("name", "date_pattern", "amount", "currency", "type")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(headers))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _valid_row(
    *,
    name: str,
    date_pattern: str = "10..",
    amount: str = "5000",
    currency: str = "USD",
    entry_type: str = "income",
) -> dict[str, str]:
    return {
        "name": name,
        "date_pattern": date_pattern,
        "amount": amount,
        "currency": currency,
        "type": entry_type,
    }


@pytest.fixture
def sample_plan(plan_repository: SqlitePlanRepository) -> str:
    plan = plan_repository.create(
        PlanCreateDto(name="Test Plan", base_currency="USD", initial_balance=1000.0)
    )
    return plan.id


@pytest.fixture
def import_vm(entry_repository: object) -> ImportViewModel:
    return ImportViewModel(entry_repository, ImportService())


@pytest.fixture
def entries_vm(entry_repository: object) -> EntriesViewModel:
    return EntriesViewModel(entry_repository)


@pytest.mark.integration
def test_import_file_increases_entries_view_model_row_count(
    qtbot: object,
    import_vm: ImportViewModel,
    entries_vm: EntriesViewModel,
    sample_plan: str,
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "entries.csv"
    _write_csv(
        csv_path,
        [
            _valid_row(name="Salary"),
            _valid_row(name="Bonus", date_pattern="15..", amount="250"),
            _valid_row(name="Rent", date_pattern="1..", amount="1200", entry_type="expense"),
        ],
    )
    entries_vm.loadEntries(sample_plan)
    assert entries_vm.entryListModel.rowCount() == 0

    import_vm.importFile(str(csv_path), sample_plan, {})

    with qtbot.waitSignal(import_vm.importCompleted, timeout=5000):  # type: ignore[attr-defined]
        pass

    entries_vm.loadEntries(sample_plan)

    assert import_vm.error == ""
    assert import_vm.importedCount == 3
    assert entries_vm.entryListModel.rowCount() == 3


@pytest.mark.integration
def test_import_file_invalid_path_sets_error_without_changing_row_count(
    qtbot: object,
    import_vm: ImportViewModel,
    entries_vm: EntriesViewModel,
    sample_plan: str,
) -> None:
    entries_vm.loadEntries(sample_plan)
    assert entries_vm.entryListModel.rowCount() == 0

    import_vm.importFile(str(Path("/nonexistent/import-file.csv")), sample_plan, {})

    with qtbot.waitSignal(import_vm.errorChanged, timeout=5000):  # type: ignore[attr-defined]
        pass

    entries_vm.loadEntries(sample_plan)

    assert import_vm.error != ""
    assert entries_vm.entryListModel.rowCount() == 0


@pytest.mark.integration
def test_import_file_emits_incremental_progress_for_large_file(
    qtbot: object,
    import_vm: ImportViewModel,
    sample_plan: str,
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "large.csv"
    _write_csv(
        csv_path,
        [_valid_row(name=f"Entry {index}") for index in range(15)],
    )
    progress_values: list[float] = []
    import_vm.progressChanged.connect(lambda: progress_values.append(import_vm.progress))

    import_vm.importFile(str(csv_path), sample_plan, {})

    with qtbot.waitSignal(import_vm.importCompleted, timeout=5000):  # type: ignore[attr-defined]
        pass

    assert import_vm.error == ""
    assert import_vm.importedCount == 15
    assert len(progress_values) >= 2
    assert any(0.0 < value < 1.0 for value in progress_values)
    assert progress_values[-1] == 1.0
