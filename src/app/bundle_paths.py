from __future__ import annotations

import sys
from pathlib import Path


def runtime_root() -> Path:
    """Return the directory that holds bundled runtime assets (qml/, alembic.ini, …).

    In PyInstaller one-dir / .app builds this is ``sys._MEIPASS`` (``Contents/Frameworks`` on
    macOS). In development it is the repository root (parent of ``main.py`` / ``src/``).
    """
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
        return Path(sys.executable).resolve().parent

    # src/app/bundle_paths.py → parents[2] == repository root
    return Path(__file__).resolve().parents[2]
