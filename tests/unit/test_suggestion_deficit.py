from __future__ import annotations

from datetime import date

import pytest

from src.domain.entities import Entry, EntryType, SimulationParams, SimulationResult
from src.domain.suggestion_deficit import (
    DEFICIT_ANALYZER_FUNCS,
    analyze_deficit_scenario,
)
from src.domain.suggestion_simulation import (
    apply_uniform_expense_cut,
    minimum_opening_balance_buffer,
    simulate_entries,
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
        category="general",
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
    engine = SuggestionEngine(analyzers=list(DEFICIT_ANALYZER_FUNCS))
    return engine.analyze(entries, result), result


@pytest.mark.unit
def test_deficit_analyzers_return_empty_when_no_shortfall() -> None:
    start = date(2026, 1, 1)
    end = date(2026, 3, 31)
    params = _params(start=start, end=end, initial_balance=1000.0)
    entries = [
        _entry(
            entry_id="income-1",
            entry_type=EntryType.INCOME,
            name="Salary",
            amount=3000.0,
            date_pattern="1..",
        ),
        _entry(
            entry_id="expense-1",
            entry_type=EntryType.EXPENSE,
            name="Rent",
            amount=1000.0,
            date_pattern="5..",
        ),
    ]

    suggestions, result = _analyze(entries, params)

    assert result.first_deficit_date is None
    assert suggestions == ()
    assert list(analyze_deficit_scenario(entries, result)) == []


@pytest.mark.unit
def test_single_large_expense_emits_multiple_deficit_kinds() -> None:
    start = date(2026, 1, 1)
    end = date(2026, 3, 31)
    params = _params(start=start, end=end, initial_balance=200.0)
    entries = [
        _entry(
            entry_id="income-1",
            entry_type=EntryType.INCOME,
            name="Salary",
            amount=500.0,
            date_pattern="1..",
        ),
        _entry(
            entry_id="expense-recurring",
            entry_type=EntryType.EXPENSE,
            name="Rent",
            amount=900.0,
            date_pattern="5..",
        ),
        _entry(
            entry_id="expense-1",
            entry_type=EntryType.EXPENSE,
            name="Equipment",
            amount=400.0,
            date_pattern="3.1.2026",
        ),
    ]

    suggestions, result = _analyze(entries, params)

    assert result.first_deficit_date is not None
    kinds = {suggestion.kind for suggestion in suggestions}
    assert SuggestionKind.AVOID_DEFICIT in kinds
    assert SuggestionKind.REDUCE_SPEND in kinds
    assert SuggestionKind.INCREASE_INCOME in kinds
    assert SuggestionKind.BUILD_BUFFER in kinds
    assert len(kinds) >= 4

    buffer_suggestion = next(s for s in suggestions if s.kind == SuggestionKind.BUILD_BUFFER)
    expected_buffer = minimum_opening_balance_buffer(result)
    assert buffer_suggestion.impact_amount is not None
    assert buffer_suggestion.impact_amount == pytest.approx(expected_buffer)
    assert buffer_suggestion.suggested_change is not None
    assert buffer_suggestion.suggested_change.target_initial_balance == pytest.approx(
        params.initial_balance + expected_buffer,
    )


@pytest.mark.unit
def test_multi_entry_plan_deficit_suggestions_are_directionally_correct() -> None:
    start = date(2026, 1, 1)
    end = date(2026, 6, 30)
    params = _params(start=start, end=end, initial_balance=500.0)
    entries = [
        _entry(
            entry_id="income-1",
            entry_type=EntryType.INCOME,
            name="Retainers",
            amount=1000.0,
            date_pattern="1..",
        ),
        _entry(
            entry_id="expense-rent",
            entry_type=EntryType.EXPENSE,
            name="Office rent",
            amount=900.0,
            date_pattern="5..",
        ),
        _entry(
            entry_id="expense-marketing",
            entry_type=EntryType.EXPENSE,
            name="Marketing",
            amount=800.0,
            date_pattern="10..",
        ),
        _entry(
            entry_id="expense-onetime",
            entry_type=EntryType.EXPENSE,
            name="Conference",
            amount=400.0,
            date_pattern="8.1.2026",
        ),
    ]

    suggestions, result = _analyze(entries, params)

    assert result.first_deficit_date is not None
    assert len(suggestions) >= 4

    uniform = next(s for s in suggestions if s.kind == SuggestionKind.AVOID_DEFICIT)
    cut_percent = -uniform.suggested_change.percent_delta  # type: ignore[union-attr]
    patched = apply_uniform_expense_cut(entries, cut_percent)
    counterfactual = _run(patched, params)
    assert counterfactual.first_deficit_date is None

    targeted = [s for s in suggestions if s.kind == SuggestionKind.REDUCE_SPEND]
    assert len(targeted) <= 3
    assert all(s.related_entry_id is not None for s in targeted)

    deferrals = [s for s in suggestions if s.kind == SuggestionKind.EXTEND_RUNWAY]
    assert any(s.related_entry_id == "expense-onetime" for s in deferrals)
    assert all(s.suggested_change is None for s in deferrals)


@pytest.mark.unit
def test_inactive_entries_are_skipped_by_deficit_analyzers() -> None:
    start = date(2026, 1, 1)
    end = date(2026, 3, 31)
    params = _params(start=start, end=end, initial_balance=1000.0)
    entries = [
        _entry(
            entry_id="income-1",
            entry_type=EntryType.INCOME,
            name="Salary",
            amount=500.0,
            date_pattern="1..",
        ),
        _entry(
            entry_id="expense-active",
            entry_type=EntryType.EXPENSE,
            name="Active vendor",
            amount=1200.0,
            date_pattern="15..",
        ),
        _entry(
            entry_id="expense-inactive",
            entry_type=EntryType.EXPENSE,
            name="Inactive vendor",
            amount=5000.0,
            date_pattern="20..",
            is_active=False,
        ),
    ]

    suggestions, result = _analyze(entries, params)

    assert result.first_deficit_date is not None
    targeted_ids = {
        suggestion.related_entry_id
        for suggestion in suggestions
        if suggestion.related_entry_id is not None
    }
    assert "expense-inactive" not in targeted_ids

    inactive_only = [
        _entry(
            entry_id="expense-inactive",
            entry_type=EntryType.EXPENSE,
            name="Inactive vendor",
            amount=5000.0,
            date_pattern="20..",
            is_active=False,
        ),
    ]
    healthy = _run(inactive_only, params)
    assert healthy.first_deficit_date is None


@pytest.mark.unit
def test_opening_balance_counterfactual_clears_shortfall() -> None:
    start = date(2026, 1, 1)
    end = date(2026, 2, 28)
    params = _params(start=start, end=end, initial_balance=100.0)
    entries = [
        _entry(
            entry_id="expense-1",
            entry_type=EntryType.EXPENSE,
            name="Big bill",
            amount=250.0,
            date_pattern="10.2.2026",
        ),
    ]
    result = _run(entries, params)
    buffer = minimum_opening_balance_buffer(result)
    buffered_params = SimulationParams(
        start_date=params.start_date,
        end_date=params.end_date,
        initial_balance=params.initial_balance + buffer,
        base_currency=params.base_currency,
    )
    counterfactual = simulate_entries(entries, buffered_params, plan_id=_PLAN_ID)
    assert counterfactual.first_deficit_date is None
