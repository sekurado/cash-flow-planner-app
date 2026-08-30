#!/usr/bin/env bash
# Cursor project hook wrapper. Cwd is the repo root.
set -euo pipefail
mode="${1:?usage: review-gate.sh git|stop}"
if [[ -x .venv/bin/python ]]; then
  py=.venv/bin/python
elif command -v python3 >/dev/null 2>&1; then
  py=python3
else
  py=python
fi
exec "$py" scripts/harness/review_gate.py --hook "$mode"
