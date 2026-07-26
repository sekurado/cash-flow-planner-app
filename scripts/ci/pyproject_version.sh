#!/usr/bin/env bash
# Print the [project].version value from pyproject.toml.
#
# Usage:
#   ./scripts/ci/pyproject_version.sh [path-to-pyproject.toml]
set -euo pipefail

pyproject="${1:-pyproject.toml}"

if [[ "${pyproject}" == "-" ]]; then
  input="/dev/stdin"
elif [[ ! -f "${pyproject}" ]]; then
  echo "error: ${pyproject} not found" >&2
  exit 1
else
  input="${pyproject}"
fi

version="$(
  grep -E '^version[[:space:]]*=[[:space:]]*"' "${input}" \
    | head -1 \
    | sed -E 's/^version[[:space:]]*=[[:space:]]*"([^"]+)".*/\1/'
)"

if [[ -z "${version}" ]]; then
  echo "error: could not read version from ${pyproject}" >&2
  exit 1
fi

printf '%s' "${version}"
