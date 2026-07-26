from __future__ import annotations

from pathlib import Path

import pytest

from src.domain.entities import EntryType
from tests.e2e.conftest import E2EStack


def _entry_snapshot(entry: dict[str, object]) -> dict[str, object]:
    return {
        "entry_type": entry["entry_type"],
        "name": entry["name"],
        "date_pattern": entry["date_pattern"],
        "amount": entry["amount"],
        "currency": entry["currency"],
        "category": entry.get("category"),
        "is_active": entry["is_active"],
    }


@pytest.mark.e2e
def test_plan_export_import_round_trip_creates_new_plan_with_entries(
    qtbot: object,
    e2e_stack: E2EStack,
    tmp_path: Path,
) -> None:
    plan_vm = e2e_stack.plan_vm
    entries_vm = e2e_stack.entries_vm
    currency_vm = e2e_stack.currency_vm
    plan_import_vm = e2e_stack.plan_import_vm

    plan_vm.createPlan("Round Trip Plan", "USD", 5000.0)
    source_plan_id = plan_vm.plans[0]["id"]
    plan_vm.selectPlan(source_plan_id)

    entries_vm.createEntry(
        {
            "plan_id": source_plan_id,
            "entry_type": EntryType.INCOME.value,
            "name": "Salary",
            "date_pattern": "10..",
            "amount": 3000.0,
            "currency": "USD",
        }
    )
    entries_vm.createEntry(
        {
            "plan_id": source_plan_id,
            "entry_type": EntryType.EXPENSE.value,
            "name": "Rent",
            "date_pattern": "1..",
            "amount": 1200.0,
            "currency": "EUR",
            "category": "Housing",
            "is_active": False,
        }
    )
    entries_vm.loadEntries(source_plan_id)
    source_entries = [_entry_snapshot(entry) for entry in entries_vm.entries]

    currency_vm.createRate("EUR", "USD", 1.08)

    bundle_path = tmp_path / "round-trip.ftplan"
    plan_vm.exportPlan(source_plan_id, str(bundle_path))
    with qtbot.waitSignal(plan_vm.exportSucceeded, timeout=5000):  # type: ignore[attr-defined]
        pass
    assert plan_vm.error == ""
    assert bundle_path.is_file()

    initial_plan_count = len(plan_vm.plans)
    plan_import_vm.importFile(str(bundle_path))
    with qtbot.waitSignal(plan_import_vm.importCompleted, timeout=5000) as blocker:  # type: ignore[attr-defined]
        pass

    imported_plan_id = blocker.args[0]
    assert plan_import_vm.error == ""
    assert imported_plan_id != source_plan_id

    plan_vm.loadPlans()
    assert len(plan_vm.plans) == initial_plan_count + 1

    imported_plan = next(plan for plan in plan_vm.plans if plan["id"] == imported_plan_id)
    source_plan = next(plan for plan in plan_vm.plans if plan["id"] == source_plan_id)
    assert imported_plan["name"] == f"{source_plan['name']} (imported)"
    assert imported_plan["base_currency"] == source_plan["base_currency"]
    assert imported_plan["initial_balance"] == source_plan["initial_balance"]

    entries_vm.loadEntries(imported_plan_id)
    assert len(entries_vm.entries) == len(source_entries)
    assert sorted(
        (_entry_snapshot(entry) for entry in entries_vm.entries), key=lambda item: item["name"]
    ) == sorted(source_entries, key=lambda item: item["name"])


@pytest.mark.e2e
def test_plan_export_import_round_trip_preserves_eur_base_and_rates(
    qtbot: object,
    e2e_stack: E2EStack,
    tmp_path: Path,
) -> None:
    plan_vm = e2e_stack.plan_vm
    entries_vm = e2e_stack.entries_vm
    currency_vm = e2e_stack.currency_vm
    plan_import_vm = e2e_stack.plan_import_vm

    plan_vm.createPlan("Euro Round Trip", "EUR", 2000.0)
    source_plan_id = plan_vm.plans[0]["id"]
    plan_vm.selectPlan(source_plan_id)

    entries_vm.createEntry(
        {
            "plan_id": source_plan_id,
            "entry_type": EntryType.EXPENSE.value,
            "name": "US Supplier",
            "date_pattern": "1..",
            "amount": 500.0,
            "currency": "USD",
        }
    )
    currency_vm.createRate("USD", "EUR", 0.92)

    bundle_path = tmp_path / "euro-round-trip.ftplan"
    plan_vm.exportPlan(source_plan_id, str(bundle_path))
    with qtbot.waitSignal(plan_vm.exportSucceeded, timeout=5000):  # type: ignore[attr-defined]
        pass
    assert plan_vm.error == ""
    assert bundle_path.is_file()

    plan_import_vm.importFile(str(bundle_path))
    with qtbot.waitSignal(plan_import_vm.importCompleted, timeout=5000) as blocker:  # type: ignore[attr-defined]
        pass

    imported_plan_id = blocker.args[0]
    assert plan_import_vm.error == ""

    plan_vm.loadPlans()
    imported_plan = next(plan for plan in plan_vm.plans if plan["id"] == imported_plan_id)
    assert imported_plan["base_currency"] == "EUR"
    assert imported_plan["initial_balance"] == 2000.0

    currency_vm.loadRates("EUR")
    rates = currency_vm.rates
    usd_to_eur = next(
        rate for rate in rates if rate["from_currency"] == "USD" and rate["to_currency"] == "EUR"
    )
    assert usd_to_eur["rate"] == pytest.approx(0.92)
