from __future__ import annotations

from src.domain.entities import Entry, EntryType
from src.export.context_builder import build_entries_summary, build_override_footnotes


def _entry(
    entry_id: str,
    *,
    entry_type: EntryType = EntryType.INCOME,
    name: str = "Salary",
    amount: float = 1000.0,
    is_active: bool = True,
) -> Entry:
    return Entry(
        id=entry_id,
        plan_id="plan-1",
        entry_type=entry_type,
        name=name,
        date_pattern="1",
        amount=amount,
        currency="USD",
        created_at="2026-01-01T00:00:00Z",
        is_active=is_active,
    )


def test_build_entries_summary_counts_active_entries() -> None:
    entries = [
        _entry("income-1", entry_type=EntryType.INCOME),
        _entry("income-2", entry_type=EntryType.INCOME, is_active=False),
        _entry("expense-1", entry_type=EntryType.EXPENSE, name="Rent"),
    ]

    summary = build_entries_summary(entries)

    assert summary.active_income_count == 1
    assert summary.active_expense_count == 1
    assert summary.total_line_items == 3


def test_build_override_footnotes_lists_changed_fields() -> None:
    entries = [
        _entry("rent", entry_type=EntryType.EXPENSE, name="Rent", amount=1200.0),
        _entry("salary", entry_type=EntryType.INCOME, name="Salary", amount=5000.0),
    ]
    overrides = {
        "rent": {"amount": 900.0},
        "salary": {"is_active": False},
        "missing": {"amount": 1.0},
    }

    footnotes = build_override_footnotes(entries, overrides)

    assert footnotes == (
        "Rent: amount → 900.0",
        "Salary: active → False",
    )
