from __future__ import annotations

import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.engine import Connection

from src.app.bundle_paths import runtime_root

ALEMBIC_INI = runtime_root() / "alembic.ini"


def run_migrations(*, db_path: Path | None = None, connection: Connection | None = None) -> None:
    """Apply Alembic migrations to a database file or an existing connection."""
    if db_path is not None and connection is not None:
        msg = "Specify either db_path or connection, not both"
        raise ValueError(msg)
    if db_path is None and connection is None:
        msg = "Either db_path or connection must be provided"
        raise ValueError(msg)

    alembic_cfg = Config(str(ALEMBIC_INI))
    if connection is not None:
        alembic_cfg.attributes["connection"] = connection
    else:
        assert db_path is not None
        os.environ["FINANCIAL_TRACKER_DB_URL"] = f"sqlite:///{db_path.as_posix()}"

    command.upgrade(alembic_cfg, "head")
