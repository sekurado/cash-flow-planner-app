from __future__ import annotations

import os
from collections.abc import Generator

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import Connection
from sqlalchemy.pool import StaticPool

from src.app.identity import APPLICATION_NAME, ORGANIZATION_NAME
from src.data.migrate import run_migrations


@pytest.fixture(scope="session")
def qt_app() -> Generator[QApplication, None, None]:
    """Provide a single QApplication for the entire test session."""
    QApplication.setOrganizationName(ORGANIZATION_NAME)
    QApplication.setApplicationName(APPLICATION_NAME)

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app  # type: ignore[misc]


@pytest.fixture
def in_memory_engine() -> Generator[Engine, None, None]:
    """Fresh in-memory SQLite engine with Alembic migrations applied."""
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

    try:
        with engine.connect() as connection:
            run_migrations(connection=connection)
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def db_conn(in_memory_engine: Engine) -> Generator[Connection, None, None]:
    """Yield a connection to the migrated in-memory database."""
    connection = in_memory_engine.connect()
    try:
        yield connection
    finally:
        connection.close()
