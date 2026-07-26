#!/usr/bin/env bash
# Shared build helpers — source from other scripts in this repo.

ensure_version() {
  if [[ -n "${VERSION:-}" ]]; then
    return 0
  fi

  local pyproject="${1:-pyproject.toml}"
  if [[ ! -f "${pyproject}" ]]; then
    echo "error: ${pyproject} not found" >&2
    return 1
  fi

  VERSION="$(
    grep -E '^version[[:space:]]*=[[:space:]]*"' "${pyproject}" \
      | head -1 \
      | sed -E 's/^version[[:space:]]*=[[:space:]]*"([^"]+)".*/\1/'
  )"

  if [[ -z "${VERSION}" ]]; then
    echo "error: could not read version from ${pyproject}" >&2
    return 1
  fi

  export VERSION
}
