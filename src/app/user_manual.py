from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QFile, QIODevice, QStandardPaths, QUrl
from PySide6.QtGui import QDesktopServices

_MANUAL_FILENAME_TEMPLATE = "CashFlowPlanner-UserManual_{locale}.pdf"
_SUPPORTED_LOCALES = ("en", "fr", "ru", "es", "de")
_FALLBACK_LOCALE = "en"


class UserManualError(Exception):
    """Raised when the bundled user manual cannot be opened."""


class UserManualNotFoundError(UserManualError):
    """Raised when no bundled manual PDF exists for the requested locale."""


class UserManualOpenError(UserManualError):
    """Raised when the system PDF viewer cannot be launched."""


def manual_qrc_path(locale: str) -> str:
    return f":/manual/{_MANUAL_FILENAME_TEMPLATE.format(locale=locale)}"


def resolve_manual_qrc_path(locale: str) -> str | None:
    """Return a qrc path for the manual, falling back to English when needed."""
    candidates: list[str] = []
    if locale in _SUPPORTED_LOCALES:
        candidates.append(locale)
    if _FALLBACK_LOCALE not in candidates:
        candidates.append(_FALLBACK_LOCALE)
    for candidate in candidates:
        qrc_path = manual_qrc_path(candidate)
        if QFile.exists(qrc_path):
            return qrc_path
    return None


def _manual_cache_dir() -> Path:
    location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation)
    cache_dir = Path(location) / "manual"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def materialize_manual_pdf(qrc_path: str) -> Path:
    """Copy a bundled qrc PDF to a cache file for the system viewer."""
    qfile = QFile(qrc_path)
    if not qfile.open(QIODevice.OpenModeFlag.ReadOnly):
        raise UserManualNotFoundError("User manual is not available.")

    data = qfile.readAll().data()
    qfile.close()
    if not data:
        raise UserManualNotFoundError("User manual is not available.")

    filename = Path(qrc_path.rsplit("/", maxsplit=1)[-1]).name
    destination = _manual_cache_dir() / filename
    destination.write_bytes(data)
    return destination


def open_user_manual(locale: str = _FALLBACK_LOCALE) -> None:
    """Open the bundled user manual in the platform PDF viewer."""
    qrc_path = resolve_manual_qrc_path(locale)
    if qrc_path is None:
        raise UserManualNotFoundError("User manual is not available.")

    pdf_path = materialize_manual_pdf(qrc_path)
    opened = QDesktopServices.openUrl(QUrl.fromLocalFile(str(pdf_path)))
    if not opened:
        raise UserManualOpenError("Could not open the user manual.")
