from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtCore import QCoreApplication, QSettings, QStandardPaths
from PySide6.QtWidgets import QApplication

from src.app.identity import (
    APPLICATION_NAME,
    DB_FILENAME,
    LEGACY_APPLICATION_NAME,
    LEGACY_DB_FILENAME,
    LEGACY_ORGANIZATION_NAME,
    ORGANIZATION_NAME,
)
from src.app.identity_migration import migrate_legacy_identity

_MIGRATION_FLAG_KEY = "identityMigrated"
_TEST_SETTINGS_KEY = "cfpIdentityMigrationTest"


def _clear_migration_flag(org: str, app: str) -> None:
    for fmt in (QSettings.Format.NativeFormat, QSettings.Format.IniFormat):
        QSettings.setDefaultFormat(fmt)
        settings = QSettings(org, app)
        settings.remove(_MIGRATION_FLAG_KEY)
        settings.sync()


def _app_data_location(org: str, app: str) -> Path:
    prev_org = QCoreApplication.organizationName()
    prev_app = QCoreApplication.applicationName()
    QCoreApplication.setOrganizationName(org)
    QCoreApplication.setApplicationName(app)
    location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    QCoreApplication.setOrganizationName(prev_org)
    QCoreApplication.setApplicationName(prev_app)
    if not location:
        msg = "Could not resolve AppDataLocation in test"
        raise RuntimeError(msg)
    return Path(location)


@pytest.fixture
def isolated_identity_env(tmp_path: Path, qt_app: QApplication) -> Path:
    _ = qt_app
    QStandardPaths.setTestModeEnabled(True)
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(tmp_path))
    _clear_migration_flag(ORGANIZATION_NAME, APPLICATION_NAME)
    _clear_migration_flag(LEGACY_ORGANIZATION_NAME, LEGACY_APPLICATION_NAME)
    yield tmp_path
    for settings in (
        QSettings(ORGANIZATION_NAME, APPLICATION_NAME),
        QSettings(LEGACY_ORGANIZATION_NAME, LEGACY_APPLICATION_NAME),
    ):
        settings.clear()
        settings.sync()
    QSettings.setDefaultFormat(QSettings.Format.NativeFormat)
    QStandardPaths.setTestModeEnabled(False)


@pytest.mark.unit
def test_migrate_copies_legacy_qsettings(
    isolated_identity_env: Path,
    qt_app: QApplication,
) -> None:
    _ = isolated_identity_env, qt_app
    legacy_settings = QSettings(LEGACY_ORGANIZATION_NAME, LEGACY_APPLICATION_NAME)
    legacy_settings.setValue(_TEST_SETTINGS_KEY, "legacy-value")
    legacy_settings.sync()

    migrate_legacy_identity()

    new_settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
    assert new_settings.value(_TEST_SETTINGS_KEY) == "legacy-value"
    assert new_settings.value(_MIGRATION_FLAG_KEY, False, type=bool) is True


@pytest.mark.unit
def test_migrate_copies_legacy_database_and_sibling_files(
    isolated_identity_env: Path,
    qt_app: QApplication,
) -> None:
    _ = isolated_identity_env, qt_app
    legacy_dir = _app_data_location(LEGACY_ORGANIZATION_NAME, LEGACY_APPLICATION_NAME)
    new_dir = _app_data_location(ORGANIZATION_NAME, APPLICATION_NAME)
    legacy_dir.mkdir(parents=True, exist_ok=True)
    (legacy_dir / LEGACY_DB_FILENAME).write_text("legacy-db", encoding="utf-8")
    (legacy_dir / "crash.log").write_text("legacy-crash", encoding="utf-8")

    migrate_legacy_identity()

    assert (new_dir / DB_FILENAME).read_text(encoding="utf-8") == "legacy-db"
    assert (new_dir / "crash.log").read_text(encoding="utf-8") == "legacy-crash"


@pytest.mark.unit
def test_migrate_is_idempotent(isolated_identity_env: Path, qt_app: QApplication) -> None:
    _ = isolated_identity_env, qt_app
    legacy_settings = QSettings(LEGACY_ORGANIZATION_NAME, LEGACY_APPLICATION_NAME)
    legacy_settings.setValue(_TEST_SETTINGS_KEY, "legacy-value")
    legacy_settings.sync()

    migrate_legacy_identity()
    new_settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
    new_settings.setValue(_TEST_SETTINGS_KEY, "current-value")
    new_settings.sync()

    legacy_settings.setValue(_TEST_SETTINGS_KEY, "legacy-value")
    legacy_settings.sync()

    migrate_legacy_identity()

    assert new_settings.value(_TEST_SETTINGS_KEY) == "current-value"
