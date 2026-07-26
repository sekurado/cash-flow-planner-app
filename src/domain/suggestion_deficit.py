"""Deficit-avoidance analyzers for the cash-flow suggestions engine."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import date, timedelta

from src.domain.date_pattern import PatternType, expand_pattern, parse_pattern
from src.domain.entities import Entry, EntryType, SimulationResult
from src.domain.suggestion_messages import (
    suggestion_copy_fields,
    suggestion_defer_expense_detail,
    suggestion_defer_expense_title,
    suggestion_income_boost_detail,
    suggestion_income_boost_title,
    suggestion_opening_balance_detail,
    suggestion_opening_balance_title,
    suggestion_top_expense_detail,
    suggestion_top_expense_title,
    suggestion_uniform_cut_detail,
    suggestion_uniform_cut_title,
)
from src.domain.suggestion_simulation import (
    apply_entry_amount_delta,
    apply_income_boost,
    apply_opening_balance,
    apply_uniform_expense_cut,
    binary_search_minimum,
    clears_deficit,
    horizon_month_count,
    minimum_opening_balance_buffer,
    simulate_entries,
)
from src.domain.suggestions import (
    Analyzer,
    SuggestedChange,
    Suggestion,
    SuggestionKind,
    compute_suggestion_id,
)

_TOP_EXPENSE_TARGET_COUNT = 3
_DEFICIT_LOOKBACK_DAYS = 30


def analyze_uniform_expense_cut(
    entries: Sequence[Entry],
    result: SimulationResult,
) -> Iterable[Suggestion]:
    if result.first_deficit_date is None:
        return ()

    recurring_expenses = [
        entry
        for entry in entries
        if entry.is_active and entry.entry_type == EntryType.EXPENSE and _is_recurring(entry)
    ]
    if not recurring_expenses:
        return ()

    params = result.params
    plan_id = result.plan_id

    def clears_at_percent(cut_percent: float) -> bool:
        patched = apply_uniform_expense_cut(entries, cut_percent)
        return clears_deficit(patched, params, plan_id=plan_id)

    cut_percent = binary_search_minimum(low=0.0, high=100.0, predicate=clears_at_percent)
    if cut_percent is None or cut_percent <= 0:
        return ()

    baseline_events = simulate_entries(entries, params, plan_id=plan_id)
    patched_events = simulate_entries(
        apply_uniform_expense_cut(entries, cut_percent),
        params,
        plan_id=plan_id,
    )
    impact = patched_events.final_balance - baseline_events.final_balance
    monthly_savings = _estimate_uniform_monthly_savings(recurring_expenses, cut_percent)
    currency = params.base_currency

    title_msg = suggestion_uniform_cut_title(cut_percent)
    detail_msg = suggestion_uniform_cut_detail(cut_percent, monthly_savings, currency)

    return (
        Suggestion(
            id=compute_suggestion_id("uniform_expense_cut", f"{cut_percent:.2f}"),
            kind=SuggestionKind.AVOID_DEFICIT,
            priority=5,
            impact_amount=impact,
            impact_currency=currency,
            suggested_change=SuggestedChange(percent_delta=-cut_percent),
            **suggestion_copy_fields(title_msg, detail_msg),
        ),
    )


def analyze_top_expense_targets(
    entries: Sequence[Entry],
    result: SimulationResult,
) -> Iterable[Suggestion]:
    deficit_date = result.first_deficit_date
    if deficit_date is None:
        return ()

    params = result.params
    plan_id = result.plan_id
    ranked = _rank_expense_entries_before_deficit(entries, params, deficit_date)
    suggestions: list[Suggestion] = []

    for entry, _weight in ranked[:_TOP_EXPENSE_TARGET_COUNT]:
        cut_amount = _minimum_entry_cut(entries, entry.id, params, plan_id)
        if cut_amount is None or cut_amount <= 0:
            continue

        baseline = simulate_entries(entries, params, plan_id=plan_id)
        patched = simulate_entries(
            apply_entry_amount_delta(entries, entry.id, -cut_amount),
            params,
            plan_id=plan_id,
        )
        impact = patched.final_balance - baseline.final_balance
        currency = params.base_currency

        title_msg = suggestion_top_expense_title(entry.name)
        detail_msg = suggestion_top_expense_detail(entry.name, cut_amount, currency)

        suggestions.append(
            Suggestion(
                id=compute_suggestion_id("top_expense", entry.id, f"{cut_amount:.2f}"),
                kind=SuggestionKind.REDUCE_SPEND,
                priority=8,
                impact_amount=impact,
                impact_currency=currency,
                related_entry_id=entry.id,
                suggested_change=SuggestedChange(amount_delta=-cut_amount),
                **suggestion_copy_fields(title_msg, detail_msg),
            ),
        )

    return suggestions


def analyze_minimum_income_boost(
    entries: Sequence[Entry],
    result: SimulationResult,
) -> Iterable[Suggestion]:
    if result.first_deficit_date is None:
        return ()

    recurring_income = [
        entry
        for entry in entries
        if entry.is_active and entry.entry_type == EntryType.INCOME and _is_recurring(entry)
    ]
    if not recurring_income:
        return ()

    params = result.params
    plan_id = result.plan_id

    def clears_at_boost(monthly_boost: float) -> bool:
        patched = apply_income_boost(entries, monthly_boost)
        return clears_deficit(patched, params, plan_id=plan_id)

    max_boost = _estimate_max_monthly_boost_need(entries, params, plan_id)
    max_cap = 1_000_000.0
    while max_boost < max_cap and not clears_at_boost(max_boost):
        max_boost *= 2.0
    if not clears_at_boost(max_boost):
        return ()

    monthly_boost = binary_search_minimum(low=0.0, high=max_boost, predicate=clears_at_boost)
    if monthly_boost is None or monthly_boost <= 0:
        return ()

    baseline = simulate_entries(entries, params, plan_id=plan_id)
    patched = simulate_entries(apply_income_boost(entries, monthly_boost), params, plan_id=plan_id)
    impact = patched.final_balance - baseline.final_balance
    currency = params.base_currency

    title_msg = suggestion_income_boost_title(monthly_boost, currency)
    detail_msg = suggestion_income_boost_detail(monthly_boost, currency)

    return (
        Suggestion(
            id=compute_suggestion_id("income_boost", f"{monthly_boost:.2f}"),
            kind=SuggestionKind.INCREASE_INCOME,
            priority=10,
            impact_amount=impact,
            impact_currency=currency,
            suggested_change=SuggestedChange(amount_delta=monthly_boost / len(recurring_income)),
            **suggestion_copy_fields(title_msg, detail_msg),
        ),
    )


def analyze_opening_balance_buffer(
    entries: Sequence[Entry],
    result: SimulationResult,
) -> Iterable[Suggestion]:
    if result.first_deficit_date is None:
        return ()

    buffer_amount = minimum_opening_balance_buffer(result)
    if buffer_amount <= 0:
        return ()

    params = result.params
    plan_id = result.plan_id
    target_balance = params.initial_balance + buffer_amount
    patched_params = apply_opening_balance(params, target_balance)

    if not clears_deficit(entries, patched_params, plan_id=plan_id):
        return ()

    baseline = simulate_entries(entries, params, plan_id=plan_id)
    patched = simulate_entries(entries, patched_params, plan_id=plan_id)
    impact = patched.final_balance - baseline.final_balance
    currency = params.base_currency

    title_msg = suggestion_opening_balance_title(buffer_amount, currency)
    detail_msg = suggestion_opening_balance_detail(buffer_amount, currency)

    return (
        Suggestion(
            id=compute_suggestion_id("opening_balance", f"{buffer_amount:.2f}"),
            kind=SuggestionKind.BUILD_BUFFER,
            priority=12,
            impact_amount=impact,
            impact_currency=currency,
            suggested_change=SuggestedChange(target_initial_balance=target_balance),
            **suggestion_copy_fields(title_msg, detail_msg),
        ),
    )


def analyze_defer_one_time_expense(
    entries: Sequence[Entry],
    result: SimulationResult,
) -> Iterable[Suggestion]:
    deficit_date = result.first_deficit_date
    if deficit_date is None:
        return ()

    window_start = deficit_date - timedelta(days=_DEFICIT_LOOKBACK_DAYS)
    params = result.params
    suggestions: list[Suggestion] = []

    for entry in entries:
        if not entry.is_active or entry.entry_type != EntryType.EXPENSE:
            continue
        if parse_pattern(entry.date_pattern).type != PatternType.ONE_TIME:
            continue

        for event in expand_pattern(entry, params.start_date, params.end_date):
            if window_start <= event.date <= deficit_date:
                title_msg = suggestion_defer_expense_title(entry.name)
                detail_msg = suggestion_defer_expense_detail(
                    entry.name,
                    event.date.isoformat(),
                    deficit_date.isoformat(),
                )
                suggestions.append(
                    Suggestion(
                        id=compute_suggestion_id(
                            "defer_one_time", entry.id, event.date.isoformat()
                        ),
                        kind=SuggestionKind.EXTEND_RUNWAY,
                        priority=15,
                        impact_amount=entry.amount,
                        impact_currency=params.base_currency,
                        related_entry_id=entry.id,
                        **suggestion_copy_fields(title_msg, detail_msg),
                    ),
                )
                break

    return suggestions


DEFICIT_ANALYZER_FUNCS: tuple[Analyzer, ...] = (
    analyze_uniform_expense_cut,
    analyze_top_expense_targets,
    analyze_minimum_income_boost,
    analyze_opening_balance_buffer,
    analyze_defer_one_time_expense,
)


def analyze_deficit_scenario(
    entries: Sequence[Entry],
    result: SimulationResult,
) -> Iterable[Suggestion]:
    """Run all deficit-avoidance analyzers when a cash shortfall is projected."""
    if result.first_deficit_date is None:
        return ()

    collected: list[Suggestion] = []
    for analyzer in DEFICIT_ANALYZER_FUNCS:
        collected.extend(analyzer(entries, result))
    return collected


def _is_recurring(entry: Entry) -> bool:
    return parse_pattern(entry.date_pattern).type != PatternType.ONE_TIME


def _estimate_uniform_monthly_savings(
    recurring_expenses: Sequence[Entry],
    cut_percent: float,
) -> float:
    factor = cut_percent / 100.0
    monthly_total = 0.0
    for entry in recurring_expenses:
        pattern = parse_pattern(entry.date_pattern)
        savings_per_occurrence = entry.amount * factor
        match pattern.type:
            case PatternType.DAILY:
                monthly_total += savings_per_occurrence * 30.0
            case PatternType.MONTHLY:
                monthly_total += savings_per_occurrence
            case PatternType.YEARLY:
                monthly_total += savings_per_occurrence / 12.0
            case PatternType.ONE_TIME:
                continue
    return monthly_total


def _rank_expense_entries_before_deficit(
    entries: Sequence[Entry],
    params: object,
    deficit_date: date,
) -> list[tuple[Entry, float]]:
    from src.domain.entities import SimulationParams

    if not isinstance(params, SimulationParams):
        msg = "params must be SimulationParams"
        raise TypeError(msg)

    weights: dict[str, float] = {}
    entry_by_id: dict[str, Entry] = {}
    for entry in entries:
        if not entry.is_active or entry.entry_type != EntryType.EXPENSE:
            continue
        entry_by_id[entry.id] = entry
        total = 0.0
        for event in expand_pattern(entry, params.start_date, params.end_date):
            if event.date <= deficit_date:
                total += event.amount
        if total > 0:
            weights[entry.id] = total

    ranked_ids = sorted(weights, key=lambda entry_id: weights[entry_id], reverse=True)
    return [(entry_by_id[entry_id], weights[entry_id]) for entry_id in ranked_ids]


def _minimum_entry_cut(
    entries: Sequence[Entry],
    entry_id: str,
    params: object,
    plan_id: str,
) -> float | None:
    from src.domain.entities import SimulationParams

    if not isinstance(params, SimulationParams):
        msg = "params must be SimulationParams"
        raise TypeError(msg)

    entry = next((item for item in entries if item.id == entry_id), None)
    if entry is None:
        return None

    max_cut = entry.amount

    def clears_at_cut(cut_amount: float) -> bool:
        patched = apply_entry_amount_delta(entries, entry_id, -cut_amount)
        return clears_deficit(patched, params, plan_id=plan_id)

    return binary_search_minimum(low=0.0, high=max_cut, predicate=clears_at_cut)


def _estimate_max_monthly_boost_need(
    entries: Sequence[Entry],
    params: object,
    plan_id: str,
) -> float:
    from src.domain.entities import SimulationParams

    if not isinstance(params, SimulationParams):
        msg = "params must be SimulationParams"
        raise TypeError(msg)

    baseline = simulate_entries(entries, params, plan_id=plan_id)
    min_closing = min((day.closing_balance for day in baseline.daily_balances), default=0.0)
    shortfall = max(0.0, -min_closing)
    months = horizon_month_count(params)
    monthly_income = _estimate_monthly_recurring_total(entries, EntryType.INCOME)
    monthly_expense = _estimate_monthly_recurring_total(entries, EntryType.EXPENSE)
    recurring_gap = max(0.0, monthly_expense - monthly_income)
    return max(shortfall / months, recurring_gap) + 1.0


def _estimate_monthly_recurring_total(
    entries: Sequence[Entry],
    entry_type: EntryType,
) -> float:
    monthly_total = 0.0
    for entry in entries:
        if not entry.is_active or entry.entry_type != entry_type:
            continue
        pattern = parse_pattern(entry.date_pattern)
        match pattern.type:
            case PatternType.DAILY:
                monthly_total += entry.amount * 30.0
            case PatternType.MONTHLY:
                monthly_total += entry.amount
            case PatternType.YEARLY:
                monthly_total += entry.amount / 12.0
            case PatternType.ONE_TIME:
                continue
    return monthly_total
