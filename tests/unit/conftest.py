from __future__ import annotations

import uuid


def make_plan(**overrides: object) -> dict[str, object]:
    """Build a plan-shaped dict for unit tests (domain entities ship in Story 2)."""
    defaults: dict[str, object] = {
        "id": str(uuid.uuid4()),
        "name": "Test Plan",
        "base_currency": "USD",
        "initial_balance": 1_000.0,
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-01T00:00:00",
    }
    defaults.update(overrides)
    return defaults


def make_entry(**overrides: object) -> dict[str, object]:
    """Build an entry-shaped dict for unit tests (domain entities ship in Story 2)."""
    defaults: dict[str, object] = {
        "id": str(uuid.uuid4()),
        "plan_id": str(uuid.uuid4()),
        "entry_type": "expense",
        "name": "Test Entry",
        "date_pattern": "monthly on 1",
        "amount": 100.0,
        "currency": "USD",
        "category": None,
        "is_active": True,
        "created_at": "2026-01-01T00:00:00",
    }
    defaults.update(overrides)
    return defaults
