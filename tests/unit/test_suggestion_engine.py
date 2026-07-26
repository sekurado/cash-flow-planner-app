from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import date

import pytest

from src.domain.entities import (
    Entry,
    EntryType,
    SimulationParams,
    SimulationResult,
)
from src.domain.exceptions import SuggestionAnalysisError
from src.domain.suggestions import (
    SuggestedChange,
    Suggestion,
    SuggestionEngine,
    SuggestionKind,
    compute_suggestion_id,
)

_BASE_CURRENCY = "USD"


def _entry(
    *,
    entry_id: str = "entry-1",
    entry_type: EntryType = EntryType.EXPENSE,
    name: str = "Rent",
    amount: float = 1000.0,
) -> Entry:
    return Entry(
        id=entry_id,
        plan_id="plan-1",
        entry_type=entry_type,
        name=name,
        date_pattern="monthly on 1",
        amount=amount,
        currency=_BASE_CURRENCY,
        category="housing",
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
    )


def _empty_result() -> SimulationResult:
    start = date(2026, 1, 1)
    end = date(2026, 1, 31)
    params = SimulationParams(
        start_date=start,
        end_date=end,
        initial_balance=5000.0,
        base_currency=_BASE_CURRENCY,
    )
    return SimulationResult(
        plan_id="plan-1",
        params=params,
        daily_balances=(),
        monthly_snapshots=(),
        first_deficit_date=None,
        first_deficit_event=None,
        final_balance=5000.0,
        total_income=0.0,
        total_expense=0.0,
    )


def _suggestion(
    *,
    suggestion_id: str,
    kind: SuggestionKind = SuggestionKind.REDUCE_SPEND,
    priority: int = 10,
    title: str = "Title",
    detail: str = "Detail",
    impact_amount: float | None = 100.0,
    related_entry_id: str | None = None,
) -> Suggestion:
    return Suggestion(
        id=suggestion_id,
        kind=kind,
        priority=priority,
        title=title,
        detail=detail,
        impact_amount=impact_amount,
        impact_currency=_BASE_CURRENCY,
        related_entry_id=related_entry_id,
    )


@pytest.mark.unit
def test_analyze_with_no_analyzers_returns_empty_tuple() -> None:
    engine = SuggestionEngine()
    entries = [_entry()]

    result = engine.analyze(entries, _empty_result())

    assert result == ()


@pytest.mark.unit
def test_suggested_change_requires_exactly_one_hint() -> None:
    with pytest.raises(ValueError, match="exactly one"):
        SuggestedChange()

    with pytest.raises(ValueError, match="exactly one"):
        SuggestedChange(amount_delta=10.0, percent_delta=5.0)

    change = SuggestedChange(amount_delta=-50.0)
    assert change.amount_delta == -50.0


@pytest.mark.unit
def test_compute_suggestion_id_is_stable() -> None:
    first = compute_suggestion_id("reduce_spend", "entry-1", "420")
    second = compute_suggestion_id("reduce_spend", "entry-1", "420")
    different = compute_suggestion_id("reduce_spend", "entry-2", "420")

    assert first == second
    assert first != different
    assert len(first) == 16


@pytest.mark.unit
def test_analyze_sorts_by_priority_then_impact() -> None:
    def analyzer(
        _entries: Sequence[Entry],
        _result: SimulationResult,
    ) -> Iterable[Suggestion]:
        return [
            _suggestion(suggestion_id="low-priority-high-impact", priority=20, impact_amount=500.0),
            _suggestion(suggestion_id="high-priority-low-impact", priority=5, impact_amount=50.0),
            _suggestion(suggestion_id="high-priority-high-impact", priority=5, impact_amount=800.0),
            _suggestion(suggestion_id="mid-priority", priority=10, impact_amount=200.0),
        ]

    engine = SuggestionEngine(analyzers=[analyzer])
    ranked = engine.analyze([_entry()], _empty_result())

    assert [s.id for s in ranked] == [
        "high-priority-high-impact",
        "high-priority-low-impact",
        "mid-priority",
        "low-priority-high-impact",
    ]


@pytest.mark.unit
def test_analyze_deduplicates_by_id_keeps_better_rank() -> None:
    def first_analyzer(
        _entries: Sequence[Entry],
        _result: SimulationResult,
    ) -> Iterable[Suggestion]:
        return [
            _suggestion(
                suggestion_id="duplicate",
                priority=15,
                impact_amount=100.0,
                title="Weaker",
            ),
        ]

    def second_analyzer(
        _entries: Sequence[Entry],
        _result: SimulationResult,
    ) -> Iterable[Suggestion]:
        return [
            _suggestion(
                suggestion_id="duplicate",
                priority=5,
                impact_amount=50.0,
                title="Stronger",
            ),
        ]

    engine = SuggestionEngine(analyzers=[first_analyzer, second_analyzer])
    ranked = engine.analyze([_entry()], _empty_result())

    assert len(ranked) == 1
    assert ranked[0].title == "Stronger"


@pytest.mark.unit
def test_register_analyzer_appends_to_pipeline() -> None:
    engine = SuggestionEngine()

    def analyzer(
        _entries: Sequence[Entry],
        _result: SimulationResult,
    ) -> Iterable[Suggestion]:
        return [_suggestion(suggestion_id="registered", priority=1)]

    engine.register_analyzer(analyzer)
    ranked = engine.analyze([_entry()], _empty_result())

    assert len(ranked) == 1
    assert ranked[0].id == "registered"


@pytest.mark.unit
def test_analyze_rejects_missing_result() -> None:
    engine = SuggestionEngine()

    with pytest.raises(SuggestionAnalysisError, match="required"):
        engine.analyze([_entry()], None)  # type: ignore[arg-type]
