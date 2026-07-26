from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from src.app.version import app_version

_PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"


def _pyproject_version() -> str:
    data = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    project = data.get("project")
    assert isinstance(project, dict)
    value = project.get("version")
    assert isinstance(value, str) and value
    return value


@pytest.mark.unit
def test_app_version_reads_pyproject() -> None:
    app_version.cache_clear()
    expected = _pyproject_version()
    assert app_version() == expected
