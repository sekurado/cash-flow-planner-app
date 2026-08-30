#!/usr/bin/env python3
"""Cursor hook entry: run every check under rules/ and emit hook JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_HARNESS_DIR = Path(__file__).resolve().parent
if str(_HARNESS_DIR) not in sys.path:
    sys.path.insert(0, str(_HARNESS_DIR))

from rule import GateContext, Violation  # noqa: E402
from rules import load_rules  # noqa: E402


def run_rules(ctx: GateContext) -> list[Violation]:
    violations: list[Violation] = []
    for rule in load_rules():
        if ctx.hook not in rule.hooks:
            continue
        violations.extend(rule.check(ctx))
    return violations


def hook_git(payload: dict[str, Any]) -> dict[str, Any]:
    ctx = GateContext(hook="git", command=str(payload.get("command") or ""))
    violations = run_rules(ctx)
    if not violations:
        return {"permission": "allow"}
    message = "\n".join(item.line() for item in violations)
    return {
        "permission": "deny",
        "user_message": message,
        "agent_message": message,
    }


def hook_stop(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("status") != "completed":
        return {}
    ctx = GateContext(hook="stop", status=str(payload.get("status") or ""))
    violations = run_rules(ctx)
    if not violations:
        return {}
    body = "\n".join(item.line() for item in violations)
    return {"followup_message": "review_gate failed:\n" + body}


def _read_payload() -> dict[str, Any] | None:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data: object = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cursor review-gate hook entry.")
    parser.add_argument(
        "--hook",
        choices=("git", "stop"),
        required=True,
        help="Which Cursor hook is invoking this script.",
    )
    args = parser.parse_args(argv)
    payload = _read_payload()
    if payload is None:
        if args.hook == "git":
            message = "review_gate: hook input was not valid JSON"
            sys.stdout.write(
                json.dumps(
                    {
                        "permission": "deny",
                        "user_message": message,
                        "agent_message": message,
                    }
                )
            )
            return 0
        sys.stdout.write("{}")
        return 0
    result = hook_git(payload) if args.hook == "git" else hook_stop(payload)
    sys.stdout.write(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
