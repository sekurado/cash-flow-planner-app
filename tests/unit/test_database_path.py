from __future__ import annotations

import sys
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QCoreApplication, QStandardPaths
from PySide6.QtWidgets import QApplication

from src.app.identity import APPLICATION_NAME, DB_FILENAME, ORGANIZATION_NAME
from src.data import database


@pytest.fixture
def qt_app() -> Generator[QApplication, None, None]:
    instance = QCoreApplication.instance()
    if instance is not None and isinstance(instance, QApplication):
        yield instance
        return

    app = QApplication([])
    app.setOrganizationName(ORGANIZATION_NAME)
    app.setApplicationName(APPLICATION_NAME)
    yield app
    app.quit()


@pytest.mark.unit
def test_resolve_database_path_uses_app_data_when_frozen(
    qt_app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    install_dir = tmp_path / "install"
    meipass = tmp_path / "_MEIPASS"
    install_dir.mkdir()
    meipass.mkdir()
    fake_exe = install_dir / "CashFlowPlanner.exe"
    fake_exe.write_text("", encoding="utf-8")

    app_data = tmp_path / "AppData" / ORGANIZATION_NAME / APPLICATION_NAME
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(meipass), raising=False)
    monkeypatch.setattr(sys, "executable", str(fake_exe), raising=False)
    monkeypatch.setattr(
        QStandardPaths,
        "writableLocation",
        MagicMock(return_value=str(app_data)),
    )

    db_path = database.resolve_database_path()

    assert db_path == app_data / DB_FILENAME
    assert install_dir not in db_path.parents
    assert meipass not in db_path.parents


@pytest.mark.unit
def test_resolve_database_path_redirects_frozen_bundle_path(
    qt_app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    install_dir = tmp_path / "install"
    install_dir.mkdir()
    fake_exe = install_dir / "CashFlowPlanner.exe"
    fake_exe.write_text("", encoding="utf-8")
    bundled_db = install_dir / DB_FILENAME

    app_data = tmp_path / "AppData" / ORGANIZATION_NAME / APPLICATION_NAME
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(fake_exe), raising=False)
    monkeypatch.setattr(
        QStandardPaths,
        "writableLocation",
        MagicMock(side_effect=[str(install_dir), str(app_data)]),
    )

    db_path = database.resolve_database_path()

    assert db_path == app_data / DB_FILENAME
    assert db_path != bundled_db


@pytest.mark.unit
def test_resolve_database_path_raises_when_frozen_without_app_data(
    qt_app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    install_dir = tmp_path / "install"
    install_dir.mkdir()
    fake_exe = install_dir / "CashFlowPlanner.exe"
    fake_exe.write_text("", encoding="utf-8")

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(fake_exe), raising=False)
    monkeypatch.setattr(
        QStandardPaths,
        "writableLocation",
        MagicMock(return_value=""),
    )

    with pytest.raises(RuntimeError, match="AppDataLocation"):
        database.resolve_database_path()
