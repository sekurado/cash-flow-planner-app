"""Surplus and savings analyzers for the cash-flow suggestions engine."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence

from src.domain.date_pattern import PatternType, expand_pattern, parse_pattern
from src.domain.entities import Entry, EntryType, SimulationParams, SimulationResult
from src.domain.suggestion_messages import (
    suggestion_copy_fields,
    suggestion_largest_category_detail,
    suggestion_largest_category_title,
    suggestion_low_ending_balance_detail,
    suggestion_low_ending_balance_title,
    suggestion_positive_runway_detail,
    suggestion_positive_runway_title,
    suggestion_surplus_headroom_detail,
    suggestion_surplus_headroom_title,
)
from src.domain.suggestion_simulation import (
    apply_monthly_expense_pressure,
    average_monthly_burn,
    average_monthly_expense,
    average_monthly_income,
    binary_search_maximum,
    clears_deficit,
    horizon_month_count,
)
from src.domain.suggestions import (
    Analyzer,
    SuggestedChange,
    Suggestion,
    SuggestionKind,
    compute_suggestion_id,
)

_DISCRETIONARY_CATEGORIES: frozenset[str] = frozenset(
    {
        "marketing",
        "software",
        "professional",
        "entertainment",
        "dining",
        "travel",
        "discretionary",
        "capex",
        "licenses",
    }
)
_TOP_CATEGORY_COUNT = 3
_ENDING_BALANCE_MONTHS_THRESHOLD = 1.5
_MIN_HEADROOM = 1.0
_MIN_RUNWAY_MONTHS = 3.0


def analyze_largest_categories(
    entries: Sequence[Entry],
    result: SimulationResult,
) -> Iterable[Suggestion]:
    if result.first_deficit_date is not None:
        return ()

    category_totals = _monthly_expense_by_category(entries, result.params)
    if not category_totals:
        return ()

    discretionary = [
        (category, amount)
        for category, amount in sorted(
            category_totals.items(), key=lambda item: item[1], reverse=True
        )
        if category.lower() in _DISCRETIONARY_CATEGORIES
    ]
    ranked = discretionary[:_TOP_CATEGORY_COUNT]
    if not ranked:
        ranked = sorted(category_totals.items(), key=lambda item: item[1], reverse=True)[
            :_TOP_CATEGORY_COUNT
        ]

    currency = result.params.base_currency
    suggestions: list[Suggestion] = []
    for category, monthly_amount in ranked:
        if monthly_amount <= 0:
            continue
        title_msg = suggestion_largest_category_title(category)
        detail_msg = suggestion_largest_category_detail(category, monthly_amount, currency)
        suggestions.append(
            Suggestion(
                id=compute_suggestion_id("largest_category", category),
                kind=SuggestionKind.SAVE_MORE,
                priority=12,
                impact_amount=monthly_amount,
                impact_currency=currency,
                **suggestion_copy_fields(title_msg, detail_msg),
            ),
        )
    return suggestions


def analyze_surplus_headroom(
    entries: Sequence[Entry],
    result: SimulationResult,
) -> Iterable[Suggestion]:
    if result.first_deficit_date is not None:
        return ()

    recurring_expenses = [
        entry
        for entry in entries
        if entry.is_active
        and entry.entry_type == EntryType.EXPENSE
        and parse_pattern(entry.date_pattern).type != PatternType.ONE_TIME
    ]
    if not recurring_expenses or result.total_expense <= 0:
        return ()

    params = result.params
    plan_id = result.plan_id

    def stays_positive(monthly_pressure: float) -> bool:
        patched = apply_monthly_expense_pressure(entries, monthly_pressure)
        return clears_deficit(patched, params, plan_id=plan_id)

    if not stays_positive(0.0):
        return ()

    high = _estimate_headroom_upper_bound(entries, result, plan_id)
    monthly_savings = binary_search_maximum(low=0.0, high=high, predicate=stays_positive)
    if monthly_savings is None or monthly_savings < _MIN_HEADROOM:
        return ()

    currency = params.base_currency
    title_msg = suggestion_surplus_headroom_title(monthly_savings, currency)
    detail_msg = suggestion_surplus_headroom_detail(monthly_savings, currency)
    return (
        Suggestion(
            id=compute_suggestion_id("surplus_headroom", f"{monthly_savings:.2f}"),
            kind=SuggestionKind.SAVE_MORE,
            priority=15,
            impact_amount=monthly_savings,
            impact_currency=currency,
            suggested_change=SuggestedChange(amount_delta=-monthly_savings),
            **suggestion_copy_fields(title_msg, detail_msg),
        ),
    )


def analyze_low_ending_balance(
    entries: Sequence[Entry],
    result: SimulationResult,
) -> Iterable[Suggestion]:
    if result.first_deficit_date is not None:
        return ()

    avg_expense = average_monthly_expense(result)
    if avg_expense <= 0:
        return ()

    target_balance = _ENDING_BALANCE_MONTHS_THRESHOLD * avg_expense
    if result.final_balance >= target_balance:
        return ()

    target_buffer = target_balance - result.final_balance
    if target_buffer <= 0:
        return ()

    currency = result.params.base_currency
    target_initial = result.params.initial_balance + target_buffer

    title_msg = suggestion_low_ending_balance_title(target_buffer, currency)
    detail_msg = suggestion_low_ending_balance_detail(
        result.final_balance,
        target_balance,
        currency,
    )
    return (
        Suggestion(
            id=compute_suggestion_id("low_ending_balance", f"{target_buffer:.2f}"),
            kind=SuggestionKind.BUILD_BUFFER,
            priority=8,
            impact_amount=target_buffer,
            impact_currency=currency,
            suggested_change=SuggestedChange(target_initial_balance=target_initial),
            **suggestion_copy_fields(title_msg, detail_msg),
        ),
    )


def analyze_positive_runway(
    entries: Sequence[Entry],
    result: SimulationResult,
) -> Iterable[Suggestion]:
    if result.first_deficit_date is not None or result.final_balance <= 0:
        return ()

    monthly_burn = average_monthly_burn(result)
    if monthly_burn > 0:
        runway_months = result.final_balance / monthly_burn
    else:
        avg_expense = average_monthly_expense(result)
        if avg_expense <= 0:
            return ()
        runway_months = result.final_balance / avg_expense

    if runway_months < _MIN_RUNWAY_MONTHS:
        return ()

    currency = result.params.base_currency
    title_msg = suggestion_positive_runway_title(runway_months)
    detail_msg = suggestion_positive_runway_detail(
        runway_months,
        result.final_balance,
        currency,
    )
    return (
        Suggestion(
            id=compute_suggestion_id("positive_runway", f"{runway_months:.2f}"),
            kind=SuggestionKind.EXTEND_RUNWAY,
            priority=20,
            impact_amount=result.final_balance,
            impact_currency=currency,
            **suggestion_copy_fields(title_msg, detail_msg),
        ),
    )


SURPLUS_ANALYZER_FUNCS: tuple[Analyzer, ...] = (
    analyze_largest_categories,
    analyze_surplus_headroom,
    analyze_low_ending_balance,
    analyze_positive_runway,
)


def analyze_surplus_scenario(
    entries: Sequence[Entry],
    result: SimulationResult,
) -> Iterable[Suggestion]:
    """Run all surplus/savings analyzers when no cash shortfall is projected."""
    if result.first_deficit_date is not None:
        return ()

    collected: list[Suggestion] = []
    for analyzer in SURPLUS_ANALYZER_FUNCS:
        collected.extend(analyzer(entries, result))
    return collected


def _monthly_expense_by_category(
    entries: Sequence[Entry],
    params: SimulationParams,
) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    months = horizon_month_count(params)
    for entry in entries:
        if not entry.is_active or entry.entry_type != EntryType.EXPENSE:
            continue
        category = (entry.category or "uncategorized").lower()
        horizon_total = sum(
            event.amount for event in expand_pattern(entry, params.start_date, params.end_date)
        )
        totals[category] += horizon_total / months
    return dict(totals)


def _estimate_headroom_upper_bound(
    entries: Sequence[Entry],
    result: SimulationResult,
    plan_id: str,
) -> float:
    params = result.params
    months = horizon_month_count(params)
    recurring_gap = max(0.0, average_monthly_income(result) - average_monthly_expense(result))
    surplus_per_month = max(_MIN_HEADROOM, result.final_balance / months, recurring_gap)
    high = surplus_per_month + 1.0

    def stays_positive(monthly_pressure: float) -> bool:
        patched = apply_monthly_expense_pressure(entries, monthly_pressure)
        return clears_deficit(patched, params, plan_id=plan_id)

    max_cap = 1_000_000.0
    while high < max_cap and stays_positive(high):
        high *= 2.0
    return high
