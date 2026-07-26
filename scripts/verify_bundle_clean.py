#!/usr/bin/env python3
"""Fail if any SQLite database file is present in distributable build output."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def find_db_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*.db") if path.is_file())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify PyInstaller output contains no bundled SQLite databases.",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Directories to scan (e.g. dist/CashFlowPlanner)",
    )
    args = parser.parse_args(argv)

    offenders: list[Path] = []
    for path in args.paths:
        offenders.extend(find_db_files(path))

    if offenders:
        print("error: database files found in distributable bundle:", file=sys.stderr)
        for path in offenders:
            print(f"  {path}", file=sys.stderr)
        return 1

    print("Bundle clean: no .db files found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
