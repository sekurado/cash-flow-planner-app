from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "verify_bundle_clean.py"


def _run_verify(*paths: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *[str(path) for path in paths]],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.unit
def test_verify_bundle_clean_passes_when_no_db_files(tmp_path: Path) -> None:
    result = _run_verify(tmp_path)
    assert result.returncode == 0
    assert "Bundle clean" in result.stdout


@pytest.mark.unit
def test_verify_bundle_clean_fails_when_db_present(tmp_path: Path) -> None:
    (tmp_path / "cash_flow_planner.db").write_bytes(b"db")
    result = _run_verify(tmp_path)
    assert result.returncode == 1
    assert "cash_flow_planner.db" in result.stderr


@pytest.mark.unit
def test_verify_bundle_clean_reports_nested_db_files(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    db_path = nested / "b.db"
    db_path.write_bytes(b"db")

    result = _run_verify(tmp_path)
    assert result.returncode == 1
    assert str(db_path) in result.stderr or "b.db" in result.stderr
