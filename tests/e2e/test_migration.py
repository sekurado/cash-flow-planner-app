from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication
from sqlalchemy import inspect

from main import run_migrations
from src.data.database import create_engine_for_path, resolve_database_path

APP_TABLES = frozenset({"plans", "entries", "exchange_rates", "simulation_runs"})


@pytest.mark.e2e
def test_startup_applies_migrations(tmp_path: Path, qgui_app: QApplication) -> None:
    """Boot path in main.py applies Alembic migrations to a blank temp-file database."""
    _ = qgui_app
    db_path = resolve_database_path(data_dir=tmp_path)
    assert not db_path.exists()

    run_migrations(db_path)

    engine = create_engine_for_path(db_path)
    try:
        table_names = set(inspect(engine).get_table_names())
        assert APP_TABLES.issubset(table_names)
    finally:
        engine.dispose()
