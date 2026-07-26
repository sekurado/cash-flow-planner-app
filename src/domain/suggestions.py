"""Cash-flow suggestion analysis for simulation results.

``SuggestionEngine`` collects suggestions from registered **analyzer** callables,
deduplicates them by ``id``, and returns a ranked tuple. Analyzers are plain functions
with the signature::

    def my_analyzer(
        entries: Sequence[Entry],
        result: SimulationResult,
    ) -> Iterable[Suggestion]:
        ...

Register deficit-avoidance analyzers (Task 30_2) and surplus/savings analyzers
(Task 30_3) via ``SuggestionEngine(analyzers=[...])`` or ``register_analyzer``.
Use :data:`src.domain.suggestion_deficit.DEFICIT_ANALYZER_FUNCS` or
:func:`src.domain.suggestion_deficit.analyze_deficit_scenario` for shortfall heuristics.
Use :data:`src.domain.suggestion_surplus.SURPLUS_ANALYZER_FUNCS` or
:func:`src.domain.suggestion_surplus.analyze_surplus_scenario` for surplus heuristics.
Combine both tuples into one engine when analyzing any projection result.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from enum import StrEnum

from src.domain.entities import Entry, SimulationResult
from src.domain.exceptions import SuggestionAnalysisError

Analyzer = Callable[[Sequence[Entry], SimulationResult], Iterable["Suggestion"]]


class SuggestionKind(StrEnum):
    AVOID_DEFICIT = "avoid_deficit"
    EXTEND_RUNWAY = "extend_runway"
    REDUCE_SPEND = "reduce_spend"
    INCREASE_INCOME = "increase_income"
    BUILD_BUFFER = "build_buffer"
    SAVE_MORE = "save_more"


@dataclass(frozen=True)
class SuggestedChange:
    """Structured hint for what-if pre-fill; exactly one field must be set."""

    amount_delta: float | None = None
    percent_delta: float | None = None
    target_initial_balance: float | None = None

    def __post_init__(self) -> None:
        set_count = sum(
            1
            for value in (
                self.amount_delta,
                self.percent_delta,
                self.target_initial_balance,
            )
            if value is not None
        )
        if set_count != 1:
            msg = (
                "SuggestedChange requires exactly one of amount_delta, "
                "percent_delta, or target_initial_balance"
            )
            raise ValueError(msg)


@dataclass(frozen=True)
class Suggestion:
    id: str
    kind: SuggestionKind
    priority: int
    title: str
    detail: str
    impact_amount: float | None
    impact_currency: str
    related_entry_id: str | None = None
    suggested_change: SuggestedChange | None = None
    title_template: str = ""
    title_args: tuple[str, ...] = field(default_factory=tuple)
    detail_template: str = ""
    detail_args: tuple[str, ...] = field(default_factory=tuple)


def compute_suggestion_id(*parts: str) -> str:
    """Return a stable short hash for deduplication within a simulation run."""
    content = "|".join(parts)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def _sort_key(suggestion: Suggestion) -> tuple[int, float]:
    impact = suggestion.impact_amount if suggestion.impact_amount is not None else float("-inf")
    return (suggestion.priority, -impact)


def _deduplicate(suggestions: Iterable[Suggestion]) -> list[Suggestion]:
    by_id: dict[str, Suggestion] = {}
    for suggestion in suggestions:
        existing = by_id.get(suggestion.id)
        if existing is None or _sort_key(suggestion) < _sort_key(existing):
            by_id[suggestion.id] = suggestion
    return list(by_id.values())


class SuggestionEngine:
    """Analyze a simulation result and return ranked cash-flow suggestions."""

    def __init__(
        self,
        *,
        analyzers: Sequence[Analyzer] | None = None,
        max_suggestions: int = 10,
    ) -> None:
        self._analyzers: list[Analyzer] = list(analyzers or [])
        self.max_suggestions = max_suggestions

    def register_analyzer(self, analyzer: Analyzer) -> None:
        """Append an analyzer callable (deficit or surplus heuristic)."""
        self._analyzers.append(analyzer)

    def analyze(
        self,
        entries: Sequence[Entry],
        result: SimulationResult,
    ) -> tuple[Suggestion, ...]:
        if result is None:  # pragma: no cover — type-level guard for callers
            raise SuggestionAnalysisError("Simulation result is required for suggestion analysis")

        collected: list[Suggestion] = []
        for analyzer in self._analyzers:
            collected.extend(analyzer(entries, result))

        ranked = sorted(_deduplicate(collected), key=_sort_key)
        return tuple(ranked)
