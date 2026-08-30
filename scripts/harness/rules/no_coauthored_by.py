"""Deny git commits whose message or command contains a Co-authored-by trailer."""

from __future__ import annotations

import re

from rule import GateContext, Rule, Violation

ID = "no-coauthored-by"
MESSAGE = "don't ever add co-authored-by text in commits messages"
_COAUTHOR_RE = re.compile(r"(?i)\bCo-authored-by:")
_GIT_COMMIT_RE = re.compile(r"(?:^|[;&|]\s*)git(?:\s+-[^\s]+)*\s+commit(?:\s|$)")


def check(ctx: GateContext) -> list[Violation]:
    if ctx.hook != "git":
        return []
    if not _GIT_COMMIT_RE.search(ctx.command):
        return []
    if _COAUTHOR_RE.search(ctx.command):
        return [Violation(rule_id=ID, message=MESSAGE)]
    return []


RULE = Rule(id=ID, hooks=frozenset({"git"}), check=check)
