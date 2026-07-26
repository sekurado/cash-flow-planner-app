from __future__ import annotations

from src.domain.entities import Entry, EntryType
from src.export.models import EntriesSummary


def build_entries_summary(entries: list[Entry]) -> EntriesSummary:
    active_income_count = sum(
        1 for entry in entries if entry.is_active and entry.entry_type == EntryType.INCOME
    )
    active_expense_count = sum(
        1 for entry in entries if entry.is_active and entry.entry_type == EntryType.EXPENSE
    )
    return EntriesSummary(
        active_income_count=active_income_count,
        active_expense_count=active_expense_count,
        total_line_items=len(entries),
    )


def build_override_footnotes(
    entries: list[Entry],
    overrides: dict[str, dict[str, object]],
) -> tuple[str, ...]:
    entries_by_id = {entry.id: entry for entry in entries}
    footnotes: list[str] = []
    for entry_id, override in overrides.items():
        entry = entries_by_id.get(entry_id)
        if entry is None:
            continue
        changes: list[str] = []
        if "amount" in override:
            changes.append(f"amount → {override['amount']}")
        if "is_active" in override:
            changes.append(f"active → {override['is_active']}")
        if not changes:
            continue
        footnotes.append(f"{entry.name}: {', '.join(changes)}")
    return tuple(footnotes)
