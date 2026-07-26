from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Index,
    MetaData,
    PrimaryKeyConstraint,
    String,
    Table,
    Text,
)

metadata = MetaData()

plans = Table(
    "plans",
    metadata,
    Column("id", String, primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("name", String, nullable=False),
    Column("base_currency", String, nullable=False, default="USD"),
    Column("initial_balance", Float, nullable=False, default=0.0),
    Column("created_at", String, nullable=False),
    Column("updated_at", String, nullable=False),
)

entries = Table(
    "entries",
    metadata,
    Column("id", String, primary_key=True, default=lambda: str(uuid.uuid4())),
    Column(
        "plan_id",
        String,
        ForeignKey("plans.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("entry_type", String, nullable=False),
    Column("name", String, nullable=False),
    Column("date_pattern", String, nullable=False),
    Column("amount", Float, nullable=False),
    Column("currency", String, nullable=False),
    Column("category", String),
    Column("is_active", Boolean, nullable=False, default=True, server_default="1"),
    Column("created_at", String, nullable=False),
    Index("ix_entries_plan_id", "plan_id"),
)

exchange_rates = Table(
    "exchange_rates",
    metadata,
    Column("from_currency", String, nullable=False),
    Column("to_currency", String, nullable=False),
    Column("rate", Float, nullable=False),
    Column("updated_at", String, nullable=False),
    PrimaryKeyConstraint("from_currency", "to_currency"),
)

simulation_runs = Table(
    "simulation_runs",
    metadata,
    Column("id", String, primary_key=True, default=lambda: str(uuid.uuid4())),
    Column(
        "plan_id",
        String,
        ForeignKey("plans.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("start_date", String, nullable=False),
    Column("end_date", String, nullable=False),
    Column("result_json", Text, nullable=False),
    Column("created_at", String, nullable=False),
    Index("ix_simulation_runs_plan_id", "plan_id"),
)

audit_log = Table(
    "audit_log",
    metadata,
    Column("id", String, primary_key=True, default=lambda: str(uuid.uuid4())),
    Column(
        "plan_id",
        String,
        ForeignKey("plans.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("entity_type", String, nullable=False),
    Column("entity_id", String, nullable=False),
    Column("action", String, nullable=False),
    Column("summary", Text, nullable=False),
    Column("timestamp", String, nullable=False),
    Index("ix_audit_log_plan_id", "plan_id"),
)
