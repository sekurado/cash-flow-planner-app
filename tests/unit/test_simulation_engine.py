from __future__ import annotations

from datetime import date, timedelta

import pytest

from src.domain.entities import EntryType, NormalizedEvent, SimulationParams
from src.domain.exceptions import SimulationOverflowError
from src.domain.simulation_engine import SimulationEngine

_BASE_CURRENCY = "USD"


def _event(
    *,
    event_date: date,
    amount: float,
    entry_type: EntryType = EntryType.INCOME,
    entry_id: str = "entry-1",
    entry_name: str = "Test",
) -> NormalizedEvent:
    return NormalizedEvent(
        entry_id=entry_id,
        entry_name=entry_name,
        date=event_date,
        type=entry_type,
        normalized_amount=amount,
        base_currency=_BASE_CURRENCY,
    )


def _params(
    *,
    start: date,
    end: date,
    initial_balance: float = 1000.0,
) -> SimulationParams:
    return SimulationParams(
        start_date=start,
        end_date=end,
        initial_balance=initial_balance,
        base_currency=_BASE_CURRENCY,
    )


@pytest.mark.unit
def test_no_events_all_balances_equal_initial() -> None:
    start = date(2026, 1, 1)
    end = date(2026, 1, 7)
    initial = 500.0
    params = _params(start=start, end=end, initial_balance=initial)

    result = SimulationEngine.run([], params)

    assert result.first_deficit_date is None
    assert result.first_deficit_event is None
    assert result.total_income == 0.0
    assert result.total_expense == 0.0
    assert result.final_balance == initial
    assert len(result.daily_balances) == 7
    for daily in result.daily_balances:
        assert daily.closing_balance == initial
        assert daily.day_income == 0.0
        assert daily.day_expense == 0.0


@pytest.mark.unit
def test_income_only_balance_grows_no_deficit() -> None:
    start = date(2026, 2, 1)
    end = date(2026, 2, 5)
    params = _params(start=start, end=end, initial_balance=100.0)
    events = [
        _event(event_date=date(2026, 2, 1), amount=50.0),
        _event(event_date=date(2026, 2, 3), amount=75.0, entry_id="entry-2"),
    ]

    result = SimulationEngine.run(events, params)

    assert result.first_deficit_date is None
    assert result.total_income == 125.0
    assert result.total_expense == 0.0
    assert result.final_balance == 225.0
    assert result.daily_balances[0].closing_balance == 150.0
    assert result.daily_balances[2].closing_balance == 225.0


@pytest.mark.unit
def test_first_deficit_on_day_five() -> None:
    start = date(2026, 3, 1)
    end = date(2026, 3, 10)
    day_five = date(2026, 3, 5)
    params = _params(start=start, end=end, initial_balance=100.0)
    expense = _event(
        event_date=day_five,
        amount=150.0,
        entry_type=EntryType.EXPENSE,
        entry_id="expense-1",
        entry_name="Big bill",
    )

    result = SimulationEngine.run([expense], params)

    assert result.first_deficit_date == day_five
    assert result.first_deficit_event == expense
    day_five_balance = next(db for db in result.daily_balances if db.date == day_five)
    assert day_five_balance.closing_balance == -50.0


@pytest.mark.unit
def test_exact_zero_balance_is_not_deficit() -> None:
    start = date(2026, 4, 1)
    end = date(2026, 4, 3)
    zero_day = date(2026, 4, 2)
    params = _params(start=start, end=end, initial_balance=100.0)
    events = [
        _event(
            event_date=zero_day,
            amount=100.0,
            entry_type=EntryType.EXPENSE,
            entry_id="expense-1",
        ),
    ]

    result = SimulationEngine.run(events, params)

    assert result.first_deficit_date is None
    assert result.first_deficit_event is None
    zero_day_balance = next(db for db in result.daily_balances if db.date == zero_day)
    assert zero_day_balance.closing_balance == 0.0


@pytest.mark.unit
def test_multi_month_snapshot_totals() -> None:
    start = date(2026, 1, 1)
    end = date(2026, 3, 31)
    params = _params(start=start, end=end, initial_balance=0.0)
    events = [
        _event(event_date=date(2026, 1, 15), amount=3000.0, entry_id="salary"),
        _event(
            event_date=date(2026, 1, 20),
            amount=500.0,
            entry_type=EntryType.EXPENSE,
            entry_id="rent-jan",
        ),
        _event(event_date=date(2026, 2, 15), amount=3000.0, entry_id="salary-feb"),
        _event(
            event_date=date(2026, 2, 20),
            amount=600.0,
            entry_type=EntryType.EXPENSE,
            entry_id="rent-feb",
        ),
        _event(event_date=date(2026, 3, 15), amount=3000.0, entry_id="salary-mar"),
        _event(
            event_date=date(2026, 3, 20),
            amount=700.0,
            entry_type=EntryType.EXPENSE,
            entry_id="rent-mar",
        ),
    ]

    result = SimulationEngine.run(events, params)

    assert len(result.monthly_snapshots) == 3

    jan, feb, mar = result.monthly_snapshots
    assert jan.year == 2026 and jan.month == 1
    assert jan.total_income == 3000.0
    assert jan.total_expense == 500.0
    assert jan.net_flow == 2500.0
    assert jan.closing_balance == 2500.0
    assert jan.deficit is False

    assert feb.total_income == 3000.0
    assert feb.total_expense == 600.0
    assert feb.net_flow == 2400.0
    assert feb.closing_balance == 4900.0
    assert feb.deficit is False

    assert mar.total_income == 3000.0
    assert mar.total_expense == 700.0
    assert mar.net_flow == 2300.0
    assert mar.closing_balance == 7200.0
    assert mar.deficit is False


@pytest.mark.unit
def test_deficit_in_month_two_only() -> None:
    start = date(2026, 1, 1)
    end = date(2026, 3, 31)
    params = _params(start=start, end=end, initial_balance=1000.0)
    events = [
        _event(event_date=date(2026, 1, 31), amount=500.0, entry_id="jan-income"),
        _event(
            event_date=date(2026, 2, 28),
            amount=2000.0,
            entry_type=EntryType.EXPENSE,
            entry_id="feb-expense",
        ),
        _event(event_date=date(2026, 3, 31), amount=1000.0, entry_id="mar-income"),
    ]

    result = SimulationEngine.run(events, params)

    jan, feb, mar = result.monthly_snapshots
    assert jan.deficit is False
    assert jan.closing_balance == 1500.0
    assert feb.deficit is True
    assert feb.closing_balance == -500.0
    assert mar.deficit is False
    assert mar.closing_balance == 500.0


@pytest.mark.unit
def test_overflow_raises_simulation_overflow_error() -> None:
    start = date(2020, 1, 1)
    end = start + timedelta(days=3651)
    params = _params(start=start, end=end)

    with pytest.raises(SimulationOverflowError, match="10-year"):
        SimulationEngine.run([], params)


@pytest.mark.unit
def test_final_balance_equals_last_day_closing_balance() -> None:
    start = date(2026, 5, 1)
    end = date(2026, 5, 5)
    params = _params(start=start, end=end, initial_balance=200.0)
    events = [
        _event(event_date=date(2026, 5, 2), amount=100.0),
        _event(
            event_date=date(2026, 5, 4),
            amount=50.0,
            entry_type=EntryType.EXPENSE,
            entry_id="expense-1",
        ),
    ]

    result = SimulationEngine.run(events, params)

    assert result.final_balance == result.daily_balances[-1].closing_balance
    assert result.final_balance == 250.0
