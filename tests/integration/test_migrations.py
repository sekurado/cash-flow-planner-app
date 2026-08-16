from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.engine import Connection
from sqlalchemy.pool import StaticPool

from src.data.migrate import ALEMBIC_INI

APP_TABLES = frozenset({"plans", "entries", "exchange_rates", "simulation_runs", "audit_log"})


def _alembic_config(*, connection: Connection | None = None, db_path: Path | None = None) -> Config:
    if connection is not None and db_path is not None:
        msg = "Specify either connection or db_path, not both"
        raise ValueError(msg)
    cfg = Config(str(ALEMBIC_INI))
    if connection is not None:
        cfg.attributes["connection"] = connection
    elif db_path is not None:
        os.environ["FINANCIAL_TRACKER_DB_URL"] = f"sqlite:///{db_path.as_posix()}"
    return cfg


@pytest.fixture
def blank_memory_connection() -> Generator[Connection, None, None]:
    """Blank in-memory SQLite connection with foreign keys enabled."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection: object, _connection_record: object) -> None:
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    with engine.connect() as connection:
        yield connection

    engine.dispose()


@pytest.mark.integration
def test_alembic_history_has_four_revisions_in_order() -> None:
    script = ScriptDirectory.from_config(Config(str(ALEMBIC_INI)))
    revisions = [revision.revision for revision in script.walk_revisions()]
    assert revisions == ["0009", "0008", "0007", "0006", "0005", "0003", "0002", "0001"]


@pytest.mark.integration
def test_migrations_upgrade_and_downgrade_on_memory_db(
    blank_memory_connection: Connection,
) -> None:
    cfg = _alembic_config(connection=blank_memory_connection)

    command.upgrade(cfg, "head")
    table_names = set(inspect(blank_memory_connection).get_table_names())
    assert APP_TABLES.issubset(table_names)

    command.downgrade(cfg, "base")
    table_names = set(inspect(blank_memory_connection).get_table_names())
    assert not APP_TABLES.intersection(table_names)


@pytest.mark.integration
def test_migrations_round_trip_on_temp_file_db(tmp_path: Path) -> None:
    db_path = tmp_path / "migrations.db"
    cfg = _alembic_config(db_path=db_path)

    command.upgrade(cfg, "head")
    engine = create_engine(f"sqlite:///{db_path.as_posix()}")
    try:
        table_names = set(inspect(engine).get_table_names())
        assert APP_TABLES.issubset(table_names)
    finally:
        engine.dispose()

    command.downgrade(cfg, "base")
    engine = create_engine(f"sqlite:///{db_path.as_posix()}")
    try:
        table_names = set(inspect(engine).get_table_names())
        assert not APP_TABLES.intersection(table_names)
    finally:
        engine.dispose()


@pytest.mark.integration
def test_migration_0005_deduplicates_per_plan_rates(
    blank_memory_connection: Connection,
) -> None:
    cfg = _alembic_config(connection=blank_memory_connection)
    command.upgrade(cfg, "0003")

    blank_memory_connection.execute(
        text(
            """
            INSERT INTO plans (id, name, base_currency, initial_balance, created_at, updated_at)
            VALUES ('plan-a', 'Plan A', 'USD', 0, '2026-01-01', '2026-01-01'),
                   ('plan-b', 'Plan B', 'USD', 0, '2026-01-01', '2026-01-01')
            """
        )
    )
    blank_memory_connection.execute(
        text(
            """
            INSERT INTO exchange_rates
                (id, plan_id, from_currency, to_currency, rate, effective_date)
            VALUES
                ('rate-a', 'plan-a', 'EUR', 'USD', 1.1, '2026-01-01'),
                ('rate-b', 'plan-b', 'EUR', 'USD', 1.2, '2026-06-01')
            """
        )
    )
    blank_memory_connection.commit()

    command.upgrade(cfg, "head")

    rows = (
        blank_memory_connection.execute(
            text("SELECT from_currency, to_currency, rate, updated_at FROM exchange_rates")
        )
        .mappings()
        .all()
    )
    assert len(rows) == 1
    assert rows[0]["from_currency"] == "EUR"
    assert rows[0]["to_currency"] == "USD"
    assert rows[0]["rate"] == pytest.approx(1.2)
    assert rows[0]["updated_at"] == "2026-06-01"

    columns = {
        column["name"] for column in inspect(blank_memory_connection).get_columns("exchange_rates")
    }
    assert columns == {"from_currency", "to_currency", "rate", "updated_at"}


@pytest.mark.integration
def test_migration_0006_deletes_plans_and_non_usd_rates(
    blank_memory_connection: Connection,
) -> None:
    cfg = _alembic_config(connection=blank_memory_connection)
    command.upgrade(cfg, "0005")

    blank_memory_connection.execute(
        text(
            """
            INSERT INTO plans (id, name, base_currency, initial_balance, created_at, updated_at)
            VALUES ('plan-a', 'Plan A', 'EUR', 0, '2026-01-01', '2026-01-01')
            """
        )
    )
    blank_memory_connection.execute(
        text(
            """
            INSERT INTO entries
                (id, plan_id, entry_type, name, date_pattern, amount, currency,
                 is_active, created_at)
            VALUES
                ('entry-a', 'plan-a', 'income', 'Salary', '1..', 1000, 'USD', 1, '2026-01-01')
            """
        )
    )
    blank_memory_connection.execute(
        text(
            """
            INSERT INTO exchange_rates (from_currency, to_currency, rate, updated_at)
            VALUES ('EUR', 'USD', 1.1, '2026-01-01'),
                   ('GBP', 'EUR', 1.15, '2026-01-01')
            """
        )
    )
    blank_memory_connection.commit()

    command.upgrade(cfg, "0006")

    plan_count = blank_memory_connection.execute(text("SELECT COUNT(*) FROM plans")).scalar()
    entry_count = blank_memory_connection.execute(text("SELECT COUNT(*) FROM entries")).scalar()
    rate_rows = (
        blank_memory_connection.execute(
            text("SELECT from_currency, to_currency FROM exchange_rates")
        )
        .mappings()
        .all()
    )

    assert plan_count == 0
    assert entry_count == 0
    assert len(rate_rows) == 1
    assert rate_rows[0]["from_currency"] == "EUR"
    assert rate_rows[0]["to_currency"] == "USD"
