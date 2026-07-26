from __future__ import annotations

from datetime import date

import pytest

from src.domain.entities import Entry, EntryType, SimulationParams, SimulationResult
from src.domain.suggestion_simulation import apply_monthly_expense_pressure, simulate_entries
from src.domain.suggestion_surplus import (
    SURPLUS_ANALYZER_FUNCS,
    analyze_surplus_scenario,
)
from src.domain.suggestions import Suggestion, SuggestionEngine, SuggestionKind

_BASE_CURRENCY = "USD"
_PLAN_ID = "plan-1"


def _entry(
    *,
    entry_id: str,
    entry_type: EntryType,
    name: str,
    amount: float,
    date_pattern: str,
    category: str = "general",
    is_active: bool = True,
) -> Entry:
    return Entry(
        id=entry_id,
        plan_id=_PLAN_ID,
        entry_type=entry_type,
        name=name,
        date_pattern=date_pattern,
        amount=amount,
        currency=_BASE_CURRENCY,
        category=category,
        is_active=is_active,
        created_at="2026-01-01T00:00:00Z",
    )


def _params(
    *,
    start: date,
    end: date,
    initial_balance: float,
) -> SimulationParams:
    return SimulationParams(
        start_date=start,
        end_date=end,
        initial_balance=initial_balance,
        base_currency=_BASE_CURRENCY,
    )


def _run(entries: list[Entry], params: SimulationParams) -> SimulationResult:
    return simulate_entries(entries, params, plan_id=_PLAN_ID)


def _analyze(
    entries: list[Entry],
    params: SimulationParams,
) -> tuple[tuple[Suggestion, ...], SimulationResult]:
    result = _run(entries, params)
    engine = SuggestionEngine(analyzers=list(SURPLUS_ANALYZER_FUNCS))
    return engine.analyze(entries, result), result


@pytest.mark.unit
def test_surplus_analyzers_return_empty_when_shortfall_detected() -> None:
    start = date(2026, 1, 1)
    end = date(2026, 3, 31)
    params = _params(start=start, end=end, initial_balance=100.0)
    entries = [
        _entry(
            entry_id="income-1",
            entry_type=EntryType.INCOME,
            name="Salary",
            amount=500.0,
            date_pattern="1..",
        ),
        _entry(
            entry_id="expense-1",
            entry_type=EntryType.EXPENSE,
            name="Rent",
            amount=900.0,
            date_pattern="5..",
        ),
    ]

    suggestions, result = _analyze(entries, params)

    assert result.first_deficit_date is not None
    assert suggestions == ()
    assert list(analyze_surplus_scenario(entries, result)) == []


@pytest.mark.unit
def test_comfortable_surplus_produces_category_and_headroom_suggestions() -> None:
    start = date(2026, 1, 1)
    end = date(2026, 6, 30)
    params = _params(start=start, end=end, initial_balance=10000.0)
    entries = [
        _entry(
            entry_id="income-1",
            entry_type=EntryType.INCOME,
            name="Retainers",
            amount=5000.0,
            date_pattern="1..",
            category="revenue",
        ),
        _entry(
            entry_id="expense-rent",
            entry_type=EntryType.EXPENSE,
            name="Office rent",
            amount=1200.0,
            date_pattern="5..",
            category="facilities",
        ),
        _entry(
            entry_id="expense-marketing",
            entry_type=EntryType.EXPENSE,
            name="Marketing",
            amount=800.0,
            date_pattern="10..",
            category="marketing",
        ),
        _entry(
            entry_id="expense-software",
            entry_type=EntryType.EXPENSE,
            name="SaaS tools",
            amount=300.0,
            date_pattern="15..",
            category="software",
        ),
    ]

    suggestions, result = _analyze(entries, params)

    assert result.first_deficit_date is None
    kinds = {suggestion.kind for suggestion in suggestions}
    assert SuggestionKind.SAVE_MORE in kinds
    assert len(kinds) >= 2

    category_suggestions = [
        suggestion for suggestion in suggestions if suggestion.kind == SuggestionKind.SAVE_MORE
    ]
    assert any("marketing" in suggestion.title.lower() for suggestion in category_suggestions)

    headroom = next(
        suggestion
        for suggestion in suggestions
        if suggestion.suggested_change is not None
        and suggestion.suggested_change.amount_delta is not None
        and suggestion.suggested_change.amount_delta < 0
    )
    monthly_savings = -headroom.suggested_change.amount_delta  # type: ignore[union-attr]
    counterfactual = _run(apply_monthly_expense_pressure(entries, monthly_savings), params)
    assert counterfactual.first_deficit_date is None


@pytest.mark.unit
def test_low_ending_balance_fires_for_thin_surplus_not_comfortable_buffer() -> None:
    start = date(2026, 1, 1)
    end = date(2026, 3, 31)
    thin_entries = [
        _entry(
            entry_id="income-1",
            entry_type=EntryType.INCOME,
            name="Salary",
            amount=3000.0,
            date_pattern="1..",
            category="revenue",
        ),
        _entry(
            entry_id="expense-rent",
            entry_type=EntryType.EXPENSE,
            name="Rent",
            amount=2500.0,
            date_pattern="5..",
            category="facilities",
        ),
    ]
    thin_params = _params(start=start, end=end, initial_balance=500.0)
    thin_suggestions, thin_result = _analyze(thin_entries, thin_params)

    assert thin_result.first_deficit_date is None
    assert any(suggestion.kind == SuggestionKind.BUILD_BUFFER for suggestion in thin_suggestions)

    comfortable_params = _params(start=start, end=end, initial_balance=20000.0)
    comfortable_suggestions, comfortable_result = _analyze(thin_entries, comfortable_params)

    assert comfortable_result.first_deficit_date is None
    assert not any(
        suggestion.kind == SuggestionKind.BUILD_BUFFER for suggestion in comfortable_suggestions
    )


@pytest.mark.unit
def test_positive_runway_is_informational_for_healthy_ending_balance() -> None:
    start = date(2026, 1, 1)
    end = date(2026, 12, 31)
    params = _params(start=start, end=end, initial_balance=15000.0)
    entries = [
        _entry(
            entry_id="income-1",
            entry_type=EntryType.INCOME,
            name="Salary",
            amount=4000.0,
            date_pattern="1..",
            category="revenue",
        ),
        _entry(
            entry_id="expense-rent",
            entry_type=EntryType.EXPENSE,
            name="Rent",
            amount=1500.0,
            date_pattern="5..",
            category="facilities",
        ),
        _entry(
            entry_id="expense-ops",
            entry_type=EntryType.EXPENSE,
            name="Operations",
            amount=500.0,
            date_pattern="10..",
            category="payroll",
        ),
    ]

    suggestions, result = _analyze(entries, params)

    assert result.first_deficit_date is None
    runway = next(
        (
            suggestion
            for suggestion in suggestions
            if suggestion.kind == SuggestionKind.EXTEND_RUNWAY
        ),
        None,
    )
    assert runway is not None
    assert runway.suggested_change is None
    assert runway.impact_amount == pytest.approx(result.final_balance)


@pytest.mark.unit
def test_income_only_plan_skips_headroom_analyzer() -> None:
    start = date(2026, 1, 1)
    end = date(2026, 3, 31)
    params = _params(start=start, end=end, initial_balance=1000.0)
    entries = [
        _entry(
            entry_id="income-1",
            entry_type=EntryType.INCOME,
            name="Salary",
            amount=5000.0,
            date_pattern="1..",
            category="revenue",
        ),
    ]

    suggestions, result = _analyze(entries, params)

    assert result.first_deficit_date is None
    assert result.total_expense == 0.0
    assert not any(
        suggestion.suggested_change is not None
        and suggestion.suggested_change.amount_delta is not None
        for suggestion in suggestions
    )
