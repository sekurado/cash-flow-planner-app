from __future__ import annotations

import sys
from pathlib import Path

import pytest

from src.app.bundle_paths import runtime_root


def test_runtime_root_in_development_is_repository_root() -> None:
    root = runtime_root()
    assert (root / "pyproject.toml").is_file()
    assert (root / "qml" / "main.qml").is_file()


def test_runtime_root_in_frozen_mode_uses_meipass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    meipass = tmp_path / "bundle"
    qml_dir = meipass / "qml"
    qml_dir.mkdir(parents=True)
    (qml_dir / "main.qml").write_text("import QtQuick\n", encoding="utf-8")

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(meipass), raising=False)
    monkeypatch.setattr(sys, "executable", str(meipass / "CashFlowPlanner"), raising=False)

    assert runtime_root() == meipass.resolve()
