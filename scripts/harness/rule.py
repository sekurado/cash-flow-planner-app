"""Shared types for harness checks. Each file under rules/ exports a Rule."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

HookName = Literal["git", "stop"]


@dataclass(frozen=True)
class GateContext:
    hook: HookName
    command: str = ""
    status: str | None = None
    paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class Violation:
    rule_id: str
    message: str

    def line(self) -> str:
        return f"{self.rule_id}: {self.message}"


@dataclass(frozen=True)
class Rule:
    id: str
    hooks: frozenset[str]
    check: Callable[[GateContext], list[Violation]]
