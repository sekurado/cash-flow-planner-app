# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Cash Flow Planner Desktop (macOS, Windows, Linux)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import PySide6
from PyInstaller.building.build_main import Analysis, COLLECT, EXE, PYZ
from PyInstaller.building.osx import BUNDLE

block_cipher = None
_use_upx = sys.platform != "darwin"

_icon_dir = Path("resources/icons")
_icon_ico = _icon_dir / "app-icon.ico"
_icon_icns = _icon_dir / "app-icon.icns"

if not _icon_ico.is_file() or (sys.platform == "darwin" and not _icon_icns.is_file()):
    subprocess.run(
        [sys.executable, "scripts/generate_app_icons.py"],
        check=True,
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
    )

_exe_icon = str(_icon_ico) if sys.platform == "win32" and _icon_ico.is_file() else None
_bundle_icon = str(_icon_icns) if _icon_icns.is_file() else None

# Qt runtime plugins required for image loading, icons, and windowing.
_QT_PLUGIN_DIRS = ("imageformats", "iconengines", "platforms")
_pyside6_root = Path(PySide6.__file__).resolve().parent
_qt_plugins_root = _pyside6_root / "Qt" / "plugins"

_qt_plugin_datas = [
    (str(_qt_plugins_root / plugin_dir), f"PySide6/Qt/plugins/{plugin_dir}")
    for plugin_dir in _QT_PLUGIN_DIRS
    if (_qt_plugins_root / plugin_dir).is_dir()
]

# alembic.ini is required at runtime by src/data/migrate.py (not listed in the task
# template but needed for startup migrations inside the frozen bundle).
_app_datas = [
    ("qml/", "qml/"),
    ("src/data/migrations/", "src/data/migrations/"),
    ("src/templates/", "src/templates/"),
    ("src/export/fonts/", "src/export/fonts/"),
    ("alembic.ini", "."),
    *_qt_plugin_datas,
]

_hiddenimports = [
    "PySide6.QtCharts",
    "PySide6.QtQuickControls2",
    "sqlalchemy.dialects.sqlite",
    "alembic",
    "pydantic",
    # Alembic env.py imports logging.config; PyInstaller only traces logging from main.py.
    "logging.config",
]

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=_app_datas,
    hiddenimports=_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=["scripts/pyinstaller_runtime_hook.py"],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="CashFlowPlanner",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=_use_upx,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_exe_icon,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=_use_upx,
    upx_exclude=[],
    name="CashFlowPlanner",
)

# macOS: wrap the onedir output in a .app bundle.
# Ad-hoc / Developer ID signing is performed in scripts/build_dmg.sh after PyInstaller finishes.
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="CashFlowPlanner.app",
        icon=_bundle_icon,
        bundle_identifier="com.example.cash-flow-planner",
    )
