from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from sqlalchemy import text

from src.data import database
from src.data.database import create_engine_for_path, get_session


@pytest.mark.unit
def test_module_imports_without_qt_application() -> None:
    importlib.reload(database)


@pytest.mark.unit
def test_create_engine_for_memory() -> None:
    engine = create_engine_for_path(":memory:")
    try:
        with engine.connect() as conn:
            assert conn.execute(text("SELECT 1")).scalar() == 1
    finally:
        engine.dispose()


@pytest.mark.unit
def test_get_session_commits_on_success(tmp_path: Path) -> None:
    engine = create_engine_for_path(tmp_path / "test.db")
    try:
        with get_session(engine) as conn:
            conn.execute(text("CREATE TABLE items (id INTEGER PRIMARY KEY)"))
            conn.execute(text("INSERT INTO items (id) VALUES (1)"))

        with engine.connect() as conn:
            assert conn.execute(text("SELECT COUNT(*) FROM items")).scalar() == 1
    finally:
        engine.dispose()


@pytest.mark.unit
def test_get_session_rolls_back_on_exception(tmp_path: Path) -> None:
    engine = create_engine_for_path(tmp_path / "test.db")
    try:
        with get_session(engine) as conn:
            conn.execute(text("CREATE TABLE items (id INTEGER PRIMARY KEY)"))

        with pytest.raises(RuntimeError, match="boom"):
            with get_session(engine) as conn:
                conn.execute(text("INSERT INTO items (id) VALUES (1)"))
                raise RuntimeError("boom")

        with engine.connect() as conn:
            assert conn.execute(text("SELECT COUNT(*) FROM items")).scalar() == 0
    finally:
        engine.dispose()


@pytest.mark.unit
def test_resolve_database_path_uses_explicit_data_dir(tmp_path: Path) -> None:
    db_path = database.resolve_database_path(data_dir=tmp_path)
    assert db_path == tmp_path / database.DEFAULT_DB_FILENAME
