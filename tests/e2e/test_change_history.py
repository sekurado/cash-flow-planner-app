from __future__ import annotations

import pytest

from src.app.viewmodels.audit_log_vm import AuditLogViewModel
from src.domain.entities import EntryType
from tests.e2e.conftest import E2EStack


def _entry_payload(*, plan_id: str, name: str, amount: float) -> dict[str, object]:
    return {
        "plan_id": plan_id,
        "entry_type": EntryType.EXPENSE.value,
        "name": name,
        "date_pattern": "1..",
        "amount": amount,
        "currency": "USD",
    }


def _reload_history(audit_log_vm: AuditLogViewModel, plan_id: str) -> None:
    audit_log_vm.loadForPlan(plan_id)


def _summaries(audit_log_vm: AuditLogViewModel) -> list[str]:
    return [entry["summary"] for entry in audit_log_vm.entries]


@pytest.mark.e2e
def test_change_history_shows_plan_create_on_first_load(
    e2e_stack: E2EStack,
) -> None:
    """Opening history for a new forecast shows its creation record."""
    plan_vm = e2e_stack.plan_vm
    audit_log_vm = e2e_stack.audit_log_vm

    plan_vm.createPlan("History E2E", "USD", 5000.0)
    plan_id = plan_vm.plans[0]["id"]
    plan_vm.selectPlan(plan_id)

    _reload_history(audit_log_vm, plan_id)

    assert audit_log_vm.error == ""
    assert len(audit_log_vm.entries) == 1
    assert audit_log_vm.entries[0]["summary"] == "Created forecast 'History E2E'"
    assert audit_log_vm.entries[0]["action"] == "create"
    assert audit_log_vm.entries[0]["entity_type"] == "plan"


@pytest.mark.e2e
def test_change_history_reflects_entry_crud_newest_first(
    e2e_stack: E2EStack,
) -> None:
    """Cash-flow create, update, and delete appear in history newest-first."""
    plan_vm = e2e_stack.plan_vm
    entries_vm = e2e_stack.entries_vm
    audit_log_vm = e2e_stack.audit_log_vm

    plan_vm.createPlan("Office Forecast", "USD", 0.0)
    plan_id = plan_vm.plans[0]["id"]
    plan_vm.selectPlan(plan_id)

    entries_vm.createEntry(_entry_payload(plan_id=plan_id, name="Office rent", amount=2000.0))
    entry_id = entries_vm.entries[0]["id"]
    _reload_history(audit_log_vm, plan_id)

    assert audit_log_vm.error == ""
    assert _summaries(audit_log_vm)[0] == "Added cash flow 'Office rent' (Expense)"

    entries_vm.updateEntry(entry_id, {"amount": 2200.0})
    _reload_history(audit_log_vm, plan_id)

    assert _summaries(audit_log_vm)[0] == (
        "Updated cash flow 'Office rent': amount 2000.0 → 2200.0"
    )

    entries_vm.deleteEntry(entry_id)
    _reload_history(audit_log_vm, plan_id)

    assert _summaries(audit_log_vm)[0] == "Removed cash flow 'Office rent'"
    assert len(audit_log_vm.entries) == 4
    assert audit_log_vm.entries[-1]["summary"] == "Created forecast 'Office Forecast'"


@pytest.mark.e2e
def test_change_history_stale_until_reloaded_after_entry_edit(
    e2e_stack: E2EStack,
) -> None:
    """History panel must reload after cash-flow edits; ViewModel does not auto-sync."""
    plan_vm = e2e_stack.plan_vm
    entries_vm = e2e_stack.entries_vm
    audit_log_vm = e2e_stack.audit_log_vm

    plan_vm.createPlan("Stale Check", "USD", 0.0)
    plan_id = plan_vm.plans[0]["id"]
    plan_vm.selectPlan(plan_id)

    _reload_history(audit_log_vm, plan_id)
    count_before_edit = len(audit_log_vm.entries)
    assert count_before_edit == 1

    entries_vm.createEntry(_entry_payload(plan_id=plan_id, name="Utilities", amount=120.0))

    assert len(audit_log_vm.entries) == count_before_edit

    _reload_history(audit_log_vm, plan_id)

    assert len(audit_log_vm.entries) == count_before_edit + 1
    assert "Added cash flow 'Utilities'" in audit_log_vm.entries[0]["summary"]


@pytest.mark.e2e
def test_change_history_reflects_plan_rename(
    e2e_stack: E2EStack,
) -> None:
    """Renaming a forecast through the plan ViewModel appears in change history."""
    plan_vm = e2e_stack.plan_vm
    audit_log_vm = e2e_stack.audit_log_vm

    plan_vm.createPlan("Draft", "USD", 1000.0)
    plan_id = plan_vm.plans[0]["id"]
    plan_vm.selectPlan(plan_id)

    plan_vm.updatePlan(plan_id, {"name": "Q1 Runway"})
    _reload_history(audit_log_vm, plan_id)

    assert audit_log_vm.error == ""
    assert _summaries(audit_log_vm)[0] == "Renamed forecast to 'Q1 Runway'"
    assert len(audit_log_vm.entries) == 2
