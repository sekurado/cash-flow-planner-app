from __future__ import annotations

import pytest

from src.app.viewmodels.plan_vm import PlanViewModel
from src.data.repositories.entry_repo import EntryCreateDto, SqliteEntryRepository
from src.data.repositories.plan_repo import SqlitePlanRepository
from src.domain.entities import EntryType
from src.domain.template_service import TemplateService


@pytest.mark.integration
def test_create_plan_adds_item_to_plans(
    qt_app: object,
    plan_repository: SqlitePlanRepository,
) -> None:
    vm = PlanViewModel(plan_repository)
    assert len(vm.plans) == 0

    vm.createPlan("Test", "USD", 1000.0)

    assert vm.error == ""
    assert len(vm.plans) == 1
    plan = vm.plans[0]
    assert plan["name"] == "Test"
    assert plan["base_currency"] == "USD"
    assert plan["initial_balance"] == 1000.0
    assert isinstance(plan["id"], str)


@pytest.mark.integration
def test_delete_plan_clears_plans(
    qt_app: object,
    plan_repository: SqlitePlanRepository,
) -> None:
    vm = PlanViewModel(plan_repository)
    vm.createPlan("Test", "USD", 1000.0)
    plan_id = vm.plans[0]["id"]

    vm.deletePlan(plan_id)

    assert vm.error == ""
    assert len(vm.plans) == 0
    assert plan_repository.find_all() == []


@pytest.mark.integration
def test_update_plan_changes_name(
    qt_app: object,
    plan_repository: SqlitePlanRepository,
) -> None:
    vm = PlanViewModel(plan_repository)
    vm.createPlan("Test", "USD", 1000.0)
    plan_id = vm.plans[0]["id"]

    vm.updatePlan(plan_id, {"name": "New Name"})

    assert vm.error == ""
    assert len(vm.plans) == 1
    assert vm.plans[0]["name"] == "New Name"


@pytest.mark.integration
def test_update_plan_changes_initial_balance(
    qt_app: object,
    plan_repository: SqlitePlanRepository,
) -> None:
    vm = PlanViewModel(plan_repository)
    vm.createPlan("Test", "USD", 1000.0)
    plan_id = vm.plans[0]["id"]

    vm.updatePlan(plan_id, {"initial_balance": 2500.0})

    assert vm.error == ""
    assert vm.plans[0]["initial_balance"] == 2500.0


@pytest.mark.integration
def test_update_plan_duplicate_name_shows_error(
    qt_app: object,
    plan_repository: SqlitePlanRepository,
) -> None:
    vm = PlanViewModel(plan_repository)
    vm.createPlan("Plan A", "USD", 100.0)
    vm.createPlan("Plan B", "USD", 200.0)
    plan_b_id = vm.plans[1]["id"]

    vm.updatePlan(plan_b_id, {"name": "Plan A"})

    assert vm.error != ""
    assert vm.plans[1]["name"] == "Plan B"


@pytest.mark.integration
def test_update_plan_keeps_same_name(
    qt_app: object,
    plan_repository: SqlitePlanRepository,
) -> None:
    vm = PlanViewModel(plan_repository)
    vm.createPlan("Plan A", "USD", 100.0)
    vm.createPlan("Plan B", "USD", 200.0)
    plan_a_id = vm.plans[0]["id"]

    vm.updatePlan(plan_a_id, {"name": "Plan A", "initial_balance": 500.0})

    assert vm.error == ""
    assert vm.plans[0]["name"] == "Plan A"
    assert vm.plans[0]["initial_balance"] == 500.0


@pytest.mark.integration
def test_create_three_plans_returns_three_items(
    qt_app: object,
    plan_repository: SqlitePlanRepository,
) -> None:
    vm = PlanViewModel(plan_repository)
    vm.createPlan("Plan A", "USD", 100.0)
    vm.createPlan("Plan B", "USD", 200.0)
    vm.createPlan("Plan C", "USD", 300.0)

    assert vm.error == ""
    assert len(vm.plans) == 3
    assert len(plan_repository.find_all()) == 3
    names = {plan["name"] for plan in vm.plans}
    assert names == {"Plan A", "Plan B", "Plan C"}


@pytest.mark.integration
def test_create_plan_with_non_usd_base_currency(
    qt_app: object,
    plan_repository: SqlitePlanRepository,
) -> None:
    vm = PlanViewModel(plan_repository)

    vm.createPlan("Euro Plan", "EUR", 2500.0)

    assert vm.error == ""
    assert len(vm.plans) == 1
    plan = vm.plans[0]
    assert plan["name"] == "Euro Plan"
    assert plan["base_currency"] == "EUR"
    assert plan["initial_balance"] == 2500.0


@pytest.mark.integration
def test_delete_plan_cascades_entries(
    qt_app: object,
    plan_repository: SqlitePlanRepository,
    entry_repository: SqliteEntryRepository,
) -> None:
    vm = PlanViewModel(plan_repository)
    vm.createPlan("Test", "USD", 1000.0)
    plan_id = vm.plans[0]["id"]
    entry_repository.create(
        EntryCreateDto(
            plan_id=plan_id,
            entry_type=EntryType.INCOME,
            name="Salary",
            date_pattern="10..",
            amount=500.0,
            currency="USD",
        )
    )
    assert entry_repository.find_by_plan_id(plan_id) != []

    vm.deletePlan(plan_id)

    assert vm.error == ""
    assert len(vm.plans) == 0
    assert entry_repository.find_by_plan_id(plan_id) == []


@pytest.mark.integration
def test_create_from_template_creates_plan_and_entries(
    qt_app: object,
    plan_repository: SqlitePlanRepository,
    entry_repository: SqliteEntryRepository,
) -> None:
    template = TemplateService.load("saas_startup")
    vm = PlanViewModel(plan_repository, entry_repo=entry_repository)

    result = vm.createFromTemplate("My SaaS", "saas_startup")

    assert result is True
    assert vm.error == ""
    assert len(vm.plans) == 1
    plan = vm.plans[0]
    assert plan["name"] == "My SaaS"
    assert plan["base_currency"] == template.suggested_base_currency
    assert plan["initial_balance"] == template.suggested_initial_balance

    persisted = entry_repository.find_by_plan_id(plan["id"])
    assert len(persisted) == len(template.entries)
    for persisted_entry, template_entry in zip(persisted, template.entries, strict=True):
        assert persisted_entry.entry_type == template_entry.entry_type
        assert persisted_entry.name == template_entry.name
        assert persisted_entry.date_pattern == template_entry.date_pattern
        assert persisted_entry.amount == template_entry.amount
        assert persisted_entry.currency == template_entry.currency
        assert persisted_entry.category == template_entry.category
        assert persisted_entry.is_active == template_entry.is_active

    assert vm.selectedPlan is not None
    assert vm.selectedPlan["id"] == plan["id"]


@pytest.mark.integration
def test_create_from_template_invalid_id_sets_error(
    qt_app: object,
    plan_repository: SqlitePlanRepository,
    entry_repository: SqliteEntryRepository,
) -> None:
    vm = PlanViewModel(plan_repository, entry_repo=entry_repository)

    result = vm.createFromTemplate("My SaaS", "nonexistent_template")

    assert result is False
    assert vm.error != ""
    assert len(vm.plans) == 0


@pytest.mark.integration
def test_create_from_template_without_entry_repo_sets_error(
    qt_app: object,
    plan_repository: SqlitePlanRepository,
) -> None:
    vm = PlanViewModel(plan_repository)

    result = vm.createFromTemplate("My SaaS", "saas_startup")

    assert result is False
    assert vm.error != ""
    assert len(vm.plans) == 0


@pytest.mark.integration
def test_create_from_template_duplicate_name_allowed_like_create_plan(
    qt_app: object,
    plan_repository: SqlitePlanRepository,
    entry_repository: SqliteEntryRepository,
) -> None:
    vm = PlanViewModel(plan_repository, entry_repo=entry_repository)
    vm.createPlan("My SaaS", "USD", 1000.0)

    result = vm.createFromTemplate("My SaaS", "saas_startup")

    assert result is True
    assert vm.error == ""
    assert len(vm.plans) == 2
    names = [plan["name"] for plan in vm.plans]
    assert names.count("My SaaS") == 2
