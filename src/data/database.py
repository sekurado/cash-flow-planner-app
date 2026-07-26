from __future__ import annotations

import sys
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import Connection

from src.app.identity import DB_FILENAME, PYPROJECT_NAME

DEFAULT_DB_FILENAME = DB_FILENAME


def _resolve_app_data_directory() -> Path | None:
    """Return the OS app-data directory when Qt is available, else None."""
    try:
        from PySide6.QtCore import QCoreApplication, QStandardPaths
    except ImportError:
        return None

    if QCoreApplication.instance() is None:
        return None

    location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    if not location:
        return None

    return Path(location)


def _frozen_bundle_directories() -> list[Path]:
    """Return install and PyInstaller extract directories when running frozen."""
    if not getattr(sys, "frozen", False):
        return []

    directories: list[Path] = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        directories.append(Path(meipass).resolve())
    directories.append(Path(sys.executable).resolve().parent)
    return directories


def _is_under_any_directory(path: Path, parents: list[Path]) -> bool:
    resolved = path.resolve()
    for parent in parents:
        parent_resolved = parent.resolve()
        if resolved == parent_resolved:
            return True
        try:
            resolved.relative_to(parent_resolved)
            return True
        except ValueError:
            continue
    return False


def _reject_frozen_bundle_path(path: Path) -> Path:
    """Redirect database paths that fall inside the install or _MEIPASS tree."""
    bundle_dirs = _frozen_bundle_directories()
    if not bundle_dirs or not _is_under_any_directory(path, bundle_dirs):
        return path

    app_data_dir = _resolve_app_data_directory()
    if app_data_dir is None or _is_under_any_directory(app_data_dir, bundle_dirs):
        msg = "Database path resolved inside application bundle in frozen mode"
        raise RuntimeError(msg)

    app_data_dir.mkdir(parents=True, exist_ok=True)
    return app_data_dir / DB_FILENAME


def resolve_database_path(*, data_dir: Path | None = None) -> Path:
    """Return the filesystem path to the SQLite database file.

    When *data_dir* is provided (typical in tests), that directory is used directly.
    Otherwise the path is resolved via ``QStandardPaths.AppDataLocation`` at runtime,
    falling back to a temp directory when no Qt application is running.
    """
    if data_dir is not None:
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir / DB_FILENAME

    app_data_dir = _resolve_app_data_directory()
    if app_data_dir is not None:
        app_data_dir.mkdir(parents=True, exist_ok=True)
        return _reject_frozen_bundle_path(app_data_dir / DB_FILENAME)

    if getattr(sys, "frozen", False):
        msg = "Could not resolve AppDataLocation in frozen application"
        raise RuntimeError(msg)

    fallback_dir = Path(tempfile.gettempdir()) / PYPROJECT_NAME
    fallback_dir.mkdir(parents=True, exist_ok=True)
    return fallback_dir / DB_FILENAME


def create_engine_for_path(db_path: str | Path) -> Engine:
    """Create a SQLAlchemy engine for the given SQLite database path."""
    path_str = str(db_path)
    if path_str == ":memory:":
        url = "sqlite:///:memory:"
    else:
        path = Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{path.as_posix()}"
    engine = create_engine(url, echo=False)

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection: object, _connection_record: object) -> None:
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def create_default_engine(*, data_dir: Path | None = None) -> Engine:
    """Create an engine pointed at the default application database path."""
    return create_engine_for_path(resolve_database_path(data_dir=data_dir))


@contextmanager
def get_session(engine: Engine) -> Generator[Connection, None, None]:
    """Yield a connection that commits on success and rolls back on exception."""
    with engine.begin() as connection:
        yield connection
