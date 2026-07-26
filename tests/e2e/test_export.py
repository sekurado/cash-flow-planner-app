from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

import pytest

from src.domain.entities import EntryType
from tests.e2e.conftest import E2EStack


def _simulation_params(
    *,
    start: date,
    end: date,
    initial_balance: float,
    base_currency: str,
) -> dict[str, object]:
    return {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "initial_balance": initial_balance,
        "base_currency": base_currency,
    }


@pytest.mark.e2e
def test_export_csv_writes_monthly_snapshot_rows(
    qtbot: object,
    e2e_stack: E2EStack,
    tmp_path: Path,
) -> None:
    plan_vm = e2e_stack.plan_vm
    entries_vm = e2e_stack.entries_vm
    simulation_vm = e2e_stack.simulation_vm

    plan_vm.createPlan("Export Plan", "USD", 0.0)
    plan_id = plan_vm.plans[0]["id"]
    plan_vm.selectPlan(plan_id)

    entries_vm.createEntry(
        {
            "plan_id": plan_id,
            "entry_type": EntryType.INCOME.value,
            "name": "Salary",
            "date_pattern": "1..",
            "amount": 2000.0,
            "currency": "USD",
        }
    )
    entries_vm.createEntry(
        {
            "plan_id": plan_id,
            "entry_type": EntryType.EXPENSE.value,
            "name": "Rent",
            "date_pattern": "15..",
            "amount": 1500.0,
            "currency": "USD",
        }
    )

    params = _simulation_params(
        start=date(2026, 1, 1),
        end=date(2026, 3, 31),
        initial_balance=0.0,
        base_currency="USD",
    )
    simulation_vm.runSimulation(plan_id, params)
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass

    output = tmp_path / "output.csv"
    with qtbot.waitSignal(simulation_vm.exportSucceeded, timeout=5000):  # type: ignore[attr-defined]
        simulation_vm.exportCsv(str(output))

    assert output.exists()
    with output.open(newline="", encoding="utf-8") as file:
        rows = [row for row in csv.reader(file) if row and not row[0].startswith("#")]
    snapshot_count = simulation_vm.snapshotModel.rowCount()
    assert len(rows) - 1 == snapshot_count


@pytest.mark.e2e
def test_export_executive_pdf_creates_non_empty_file(
    qtbot: object,
    e2e_stack: E2EStack,
    tmp_path: Path,
) -> None:
    plan_vm = e2e_stack.plan_vm
    entries_vm = e2e_stack.entries_vm
    simulation_vm = e2e_stack.simulation_vm

    plan_vm.createPlan("Executive Export Plan", "USD", 0.0)
    plan_id = plan_vm.plans[0]["id"]
    plan_vm.selectPlan(plan_id)

    entries_vm.createEntry(
        {
            "plan_id": plan_id,
            "entry_type": EntryType.INCOME.value,
            "name": "Salary",
            "date_pattern": "1..",
            "amount": 2000.0,
            "currency": "USD",
        }
    )
    entries_vm.createEntry(
        {
            "plan_id": plan_id,
            "entry_type": EntryType.EXPENSE.value,
            "name": "Rent",
            "date_pattern": "15..",
            "amount": 1500.0,
            "currency": "USD",
        }
    )

    params = _simulation_params(
        start=date(2026, 1, 1),
        end=date(2026, 3, 31),
        initial_balance=0.0,
        base_currency="USD",
    )
    simulation_vm.runSimulation(plan_id, params)
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass

    output = tmp_path / "executive-report.pdf"
    with qtbot.waitSignal(simulation_vm.exportSucceeded, timeout=5000):  # type: ignore[attr-defined]
        simulation_vm.exportExecutivePdf(str(output), "Executive Export Plan", None)

    assert output.exists()
    assert output.stat().st_size > 0
    assert output.read_bytes()[:4] == b"%PDF"

    baseline_output = tmp_path / "executive-report-baseline.pdf"
    plan_vm.createPlan("Baseline Export Plan", "USD", 0.0)
    baseline_plan_id = plan_vm.plans[1]["id"]
    plan_vm.selectPlan(baseline_plan_id)
    entries_vm.createEntry(
        {
            "plan_id": baseline_plan_id,
            "entry_type": EntryType.INCOME.value,
            "name": "Small income",
            "date_pattern": "1..",
            "amount": 100.0,
            "currency": "USD",
        }
    )
    simulation_vm.runSimulation(
        baseline_plan_id,
        _simulation_params(
            start=date(2026, 1, 1),
            end=date(2026, 1, 31),
            initial_balance=0.0,
            base_currency="USD",
        ),
    )
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass
    with qtbot.waitSignal(simulation_vm.exportSucceeded, timeout=5000):  # type: ignore[attr-defined]
        simulation_vm.exportExecutivePdf(
            str(baseline_output),
            "Baseline Export Plan",
            None,
        )
    assert baseline_output.exists()
    assert output.stat().st_size > baseline_output.stat().st_size
