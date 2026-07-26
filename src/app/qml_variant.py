from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from PySide6.QtQml import QJSValue


def coerce_mapping(value: object, *, label: str = "Data") -> dict[str, Any]:
    """Normalize QML ``QVariant`` / ``QJSValue`` payloads to a plain ``dict``."""
    if isinstance(value, dict):
        return value
    if isinstance(value, QJSValue):
        converted = value.toVariant()
        if isinstance(converted, dict):
            return cast(dict[str, Any], converted)
        msg = f"{label} must be a mapping"
        raise TypeError(msg)
    if isinstance(value, Mapping):
        return dict(value)
    msg = f"{label} must be a mapping"
    raise TypeError(msg)
