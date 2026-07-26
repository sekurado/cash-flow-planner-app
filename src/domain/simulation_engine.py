from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from itertools import groupby

from src.domain.entities import (
    DailyBalance,
    EntryType,
    MonthlySnapshot,
    NormalizedEvent,
    SimulationParams,
    SimulationResult,
)
from src.domain.exceptions import SimulationOverflowError

_MAX_SIMULATION_DAYS = 3650


class SimulationEngine:
    @staticmethod
    def run(
        events: list[NormalizedEvent],
        params: SimulationParams,
        plan_id: str = "",
    ) -> SimulationResult:
        day_span = (params.end_date - params.start_date).days
        if day_span > _MAX_SIMULATION_DAYS:
            msg = (
                f"Simulation range of {day_span} days exceeds the "
                f"{_MAX_SIMULATION_DAYS}-day (10-year) limit"
            )
            raise SimulationOverflowError(msg)

        events_by_date = _group_events_by_date(events)

        daily_balances: list[DailyBalance] = []
        prev_balance = params.initial_balance
        first_deficit_date: date | None = None
        first_deficit_event: NormalizedEvent | None = None
        total_income = 0.0
        total_expense = 0.0

        cursor = params.start_date
        while cursor <= params.end_date:
            day_events = events_by_date.get(cursor, ())
            day_income = sum(e.normalized_amount for e in day_events if e.type == EntryType.INCOME)
            day_expense = sum(
                e.normalized_amount for e in day_events if e.type == EntryType.EXPENSE
            )
            closing_balance = prev_balance + day_income - day_expense

            if first_deficit_date is None and closing_balance < 0:
                first_deficit_date = cursor
                first_deficit_event = _pick_deficit_event(day_events)

            daily_balances.append(
                DailyBalance(
                    date=cursor,
                    events=day_events,
                    day_income=day_income,
                    day_expense=day_expense,
                    closing_balance=closing_balance,
                )
            )

            total_income += day_income
            total_expense += day_expense
            prev_balance = closing_balance
            cursor += timedelta(days=1)

        final_balance = (
            daily_balances[-1].closing_balance if daily_balances else params.initial_balance
        )
        monthly_snapshots = _aggregate_monthly_snapshots(daily_balances)

        return SimulationResult(
            plan_id=plan_id,
            params=params,
            daily_balances=tuple(daily_balances),
            monthly_snapshots=monthly_snapshots,
            first_deficit_date=first_deficit_date,
            first_deficit_event=first_deficit_event,
            final_balance=final_balance,
            total_income=total_income,
            total_expense=total_expense,
        )


def _aggregate_monthly_snapshots(
    daily_balances: list[DailyBalance],
) -> tuple[MonthlySnapshot, ...]:
    snapshots: list[MonthlySnapshot] = []
    for (year, month), group in groupby(
        daily_balances, key=lambda db: (db.date.year, db.date.month)
    ):
        days = list(group)
        month_income = sum(db.day_income for db in days)
        month_expense = sum(db.day_expense for db in days)
        closing = days[-1].closing_balance
        snapshots.append(
            MonthlySnapshot(
                year=year,
                month=month,
                total_income=month_income,
                total_expense=month_expense,
                net_flow=month_income - month_expense,
                closing_balance=closing,
                deficit=closing < 0,
            )
        )
    return tuple(snapshots)


def _group_events_by_date(
    events: list[NormalizedEvent],
) -> dict[date, tuple[NormalizedEvent, ...]]:
    grouped: dict[date, list[NormalizedEvent]] = defaultdict(list)
    for event in events:
        grouped[event.date].append(event)
    return {day: tuple(day_events) for day, day_events in grouped.items()}


def _pick_deficit_event(day_events: tuple[NormalizedEvent, ...]) -> NormalizedEvent | None:
    for event in day_events:
        if event.type == EntryType.EXPENSE:
            return event
    return day_events[0] if day_events else None
