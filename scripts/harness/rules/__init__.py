"""Load every Rule exported as RULE from this package."""

from __future__ import annotations

import importlib
from pathlib import Path

from rule import Rule


def load_rules() -> tuple[Rule, ...]:
    directory = Path(__file__).resolve().parent
    found: list[Rule] = []
    seen: set[str] = set()
    for path in sorted(directory.glob("*.py")):
        if path.name.startswith("_"):
            continue
        module = importlib.import_module(f"rules.{path.stem}")
        rule_obj = getattr(module, "RULE", None)
        if not isinstance(rule_obj, Rule):
            msg = f"{path.name} must export RULE as a Rule instance"
            raise TypeError(msg)
        if rule_obj.id in seen:
            msg = f"duplicate harness rule id: {rule_obj.id}"
            raise ValueError(msg)
        seen.add(rule_obj.id)
        found.append(rule_obj)
    return tuple(found)
