from __future__ import annotations

import shutil
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QSettings, QStandardPaths

from src.app.identity import (
    APPLICATION_NAME,
    DB_FILENAME,
    LEGACY_APPLICATION_NAME,
    LEGACY_DB_FILENAME,
    LEGACY_ORGANIZATION_NAME,
    ORGANIZATION_NAME,
)

_MIGRATION_FLAG_KEY = "identityMigrated"


def _app_data_location(org: str, app: str) -> Path | None:
    """Resolve AppDataLocation for *org* / *app* without changing the running identity."""
    instance = QCoreApplication.instance()
    if instance is None:
        return None

    prev_org = QCoreApplication.organizationName()
    prev_app = QCoreApplication.applicationName()
    QCoreApplication.setOrganizationName(org)
    QCoreApplication.setApplicationName(app)
    location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    QCoreApplication.setOrganizationName(prev_org)
    QCoreApplication.setApplicationName(prev_app)
    if not location:
        return None
    return Path(location)


def _merge_legacy_settings(legacy_settings: QSettings, new_settings: QSettings) -> None:
    changed = False
    for key in legacy_settings.allKeys():
        if key == _MIGRATION_FLAG_KEY:
            continue
        if new_settings.contains(key):
            continue
        new_settings.setValue(key, legacy_settings.value(key))
        changed = True
    if changed:
        new_settings.sync()


def _copy_app_data_files(legacy_data_dir: Path, new_data_dir: Path) -> None:
    legacy_db = legacy_data_dir / LEGACY_DB_FILENAME
    new_db = new_data_dir / DB_FILENAME
    if not legacy_db.is_file() or new_db.is_file():
        return

    new_data_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(legacy_db, new_db)

    for item in legacy_data_dir.iterdir():
        if item.name == LEGACY_DB_FILENAME:
            continue
        dest = new_data_dir / item.name
        if dest.exists():
            continue
        if item.is_file():
            shutil.copy2(item, dest)
        elif item.is_dir():
            shutil.copytree(item, dest)


def migrate_legacy_identity() -> None:
    """Migrate QSettings and AppData from the legacy Financial Tracker identity."""
    new_settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
    if new_settings.value(_MIGRATION_FLAG_KEY, False, type=bool):
        return

    legacy_settings = QSettings(LEGACY_ORGANIZATION_NAME, LEGACY_APPLICATION_NAME)
    _merge_legacy_settings(legacy_settings, new_settings)

    legacy_data_dir = _app_data_location(LEGACY_ORGANIZATION_NAME, LEGACY_APPLICATION_NAME)
    new_data_dir = _app_data_location(ORGANIZATION_NAME, APPLICATION_NAME)
    if legacy_data_dir is not None and new_data_dir is not None:
        _copy_app_data_files(legacy_data_dir, new_data_dir)

    new_settings.setValue(_MIGRATION_FLAG_KEY, True)
    new_settings.sync()
