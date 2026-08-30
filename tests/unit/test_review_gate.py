from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "harness" / "review_gate.py"


def _load_review_gate() -> ModuleType:
    spec = importlib.util.spec_from_file_location("review_gate", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def review_gate() -> ModuleType:
    return _load_review_gate()


@pytest.mark.unit
def test_load_rules_includes_no_coauthored_by(review_gate: ModuleType) -> None:
    ids = {rule.id for rule in review_gate.load_rules()}
    assert ids == {"no-coauthored-by"}


@pytest.mark.unit
def test_run_rules_rejects_coauthored_by(review_gate: ModuleType) -> None:
    command = """git commit -m "$(cat <<'EOF'
33_5: Tests and i18n

Closes #21
Co-authored-by: Cursor <cursoragent@cursor.com>
EOF
)"
"""
    ctx = review_gate.GateContext(hook="git", command=command)
    lines = [item.line() for item in review_gate.run_rules(ctx)]
    assert lines == ["no-coauthored-by: don't ever add co-authored-by text in commits messages"]


@pytest.mark.unit
def test_run_rules_allows_clean_message(review_gate: ModuleType) -> None:
    ctx = review_gate.GateContext(
        hook="git",
        command="git commit -m '33_5: Tests and i18n\n\nCloses #21\n'",
    )
    assert review_gate.run_rules(ctx) == []


@pytest.mark.unit
def test_hook_git_denies_commit_with_trailer(review_gate: ModuleType) -> None:
    result = review_gate.hook_git(
        {"command": "git commit -m 'fix\n\nCo-authored-by: Someone <a@b.c>'"}
    )
    assert result["permission"] == "deny"
    assert "no-coauthored-by" in result["agent_message"]


@pytest.mark.unit
def test_hook_git_allows_clean_commit(review_gate: ModuleType) -> None:
    result = review_gate.hook_git({"command": 'git commit -m "33_5: Tests and i18n"'})
    assert result == {"permission": "allow"}


@pytest.mark.unit
def test_hook_git_allows_non_commit_commands(review_gate: ModuleType) -> None:
    result = review_gate.hook_git({"command": "git status"})
    assert result == {"permission": "allow"}


@pytest.mark.unit
def test_hook_stop_completed_is_silent_until_file_rules_exist(
    review_gate: ModuleType,
) -> None:
    assert review_gate.hook_stop({"status": "completed", "loop_count": 0}) == {}


@pytest.mark.unit
def test_hook_stop_does_not_follow_up_on_abort(review_gate: ModuleType) -> None:
    assert review_gate.hook_stop({"status": "aborted", "loop_count": 0}) == {}


@pytest.mark.unit
def test_main_git_hook_reads_stdin(
    review_gate: ModuleType, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    payload = json.dumps({"command": "git commit -m 'ok'"})
    monkeypatch.setattr(review_gate.sys, "stdin", io.StringIO(payload))
    assert review_gate.main(["--hook", "git"]) == 0
    assert json.loads(capsys.readouterr().out) == {"permission": "allow"}


@pytest.mark.unit
def test_main_git_hook_denies_invalid_json(
    review_gate: ModuleType, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(review_gate.sys, "stdin", io.StringIO("{not json"))
    assert review_gate.main(["--hook", "git"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["permission"] == "deny"
