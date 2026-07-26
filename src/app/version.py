from __future__ import annotations

import tomllib
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version

from src.app.bundle_paths import runtime_root
from src.app.identity import PYPROJECT_NAME

_PACKAGE_NAME = PYPROJECT_NAME
_FALLBACK_VERSION = "0.0.0"
_PROJECT_TOML = runtime_root() / "pyproject.toml"


@lru_cache(maxsize=1)
def app_version() -> str:
    """Return the package version.

    Prefer pyproject.toml when present (dev/CI checkout) so editable installs
    stay in sync without reinstalling. Fall back to installed package metadata
    for frozen PyInstaller bundles where pyproject.toml is not shipped.
    """
    if _PROJECT_TOML.is_file():
        data = tomllib.loads(_PROJECT_TOML.read_text(encoding="utf-8"))
        project = data.get("project")
        if isinstance(project, dict):
            value = project.get("version")
            if isinstance(value, str) and value:
                return value
    try:
        return version(_PACKAGE_NAME)
    except PackageNotFoundError:
        pass
    return _FALLBACK_VERSION
