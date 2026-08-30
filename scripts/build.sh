#!/usr/bin/env bash
# One-command local build for macOS and Linux.
#
# Produces a platform installer in dist/:
#   macOS — cash-flow-planner-{version}-mac.dmg
#   Linux — cash-flow-planner-{version}-linux.AppImage
#
# Usage:
#   ./scripts/build.sh                  # auto-detect platform wrapper
#   ./scripts/build.sh --dmg            # macOS DMG only
#   ./scripts/build.sh --appimage       # Linux AppImage only
#   ./scripts/build.sh --pyinstaller-only
#
# Environment:
#   VERSION     — optional, defaults to pyproject.toml
#   OUTPUT_DIR  — optional, defaults to dist/
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck source=lib/build_version.sh
source "${ROOT}/scripts/lib/build_version.sh"

PYINSTALLER_ONLY=0
PLATFORM_MODE="auto"

usage() {
  cat <<'EOF'
Usage: ./scripts/build.sh [OPTIONS]

Options:
  --dmg               Build macOS .dmg (requires macOS)
  --appimage          Build Linux AppImage (requires Linux)
  --pyinstaller-only  Run PyInstaller only; skip installer wrapper
  -h, --help          Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dmg)
      PLATFORM_MODE="dmg"
      shift
      ;;
    --appimage)
      PLATFORM_MODE="appimage"
      shift
      ;;
    --pyinstaller-only)
      PYINSTALLER_ONLY=1
      shift
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

ensure_version
echo "Building Cash Flow Planner ${VERSION}"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "error: $1 not found — $2" >&2
    exit 1
  fi
}

install_python_deps() {
  require_command python3 "install Python 3.12+"
  python3 -m pip install --upgrade pip
  python3 -m pip install -r requirements.txt
  python3 -m pip install -e .
  case "$(uname -s)" in
    Darwin)
      python3 -m pip install -e ".[ocr-macos]"
      ;;
    Linux)
      python3 -m pip install -e ".[ocr-linux]"
      ;;
  esac
  python3 -m pip install pyinstaller pyinstaller-hooks-contrib
}

compile_i18n() {
  require_command poe "run: pip install -e \".[dev]\""
  poe i18n-bundle
}

generate_icons() {
  QT_QPA_PLATFORM=offscreen python3 scripts/generate_app_icons.py
}

generate_manual() {
  QT_QPA_PLATFORM=offscreen python3 scripts/generate_manual.py --all
}

clean_pyinstaller_output() {
  rm -rf "${ROOT}/build/CashFlowPlanner"
  rm -rf "${ROOT}/dist/CashFlowPlanner"
  rm -rf "${ROOT}/dist/CashFlowPlanner.app"
}

run_pyinstaller() {
  pyinstaller cash_flow_planner.spec --noconfirm
}

verify_bundle_clean() {
  require_command python3 "install Python 3.12+"
  python3 scripts/verify_bundle_clean.py \
    "${ROOT}/dist/CashFlowPlanner" \
    "${ROOT}/dist/CashFlowPlanner.app"
}

detect_platform_mode() {
  case "$(uname -s)" in
    Darwin)
      echo "dmg"
      ;;
    Linux)
      echo "appimage"
      ;;
    *)
      echo "error: unsupported OS for build.sh — use scripts/build.ps1 on Windows" >&2
      exit 1
      ;;
  esac
}

ensure_appimagetool() {
  local tools_dir="${ROOT}/build/tools"
  local arch
  arch="$(uname -m)"
  local tool_path="${tools_dir}/appimagetool-${arch}.AppImage"

  if command -v appimagetool >/dev/null 2>&1; then
    export APPIMAGETOOL="appimagetool"
    return 0
  fi

  if [[ -x "${tool_path}" ]]; then
    export APPIMAGETOOL="${tool_path}"
    return 0
  fi

  case "${arch}" in
    x86_64)
      local url="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
      ;;
    aarch64 | arm64)
      local url="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-aarch64.AppImage"
      ;;
    *)
      echo "error: unsupported architecture for appimagetool: ${arch}" >&2
      exit 1
      ;;
  esac

  mkdir -p "${tools_dir}"
  echo "Downloading appimagetool for ${arch}..."
  require_command curl "install curl or set APPIMAGETOOL to a local binary"
  curl -fsSL "${url}" -o "${tool_path}"
  chmod +x "${tool_path}"
  export APPIMAGETOOL="${tool_path}"
}

check_macos_prereqs() {
  require_command create-dmg "install via: brew install create-dmg"
}

check_linux_prereqs() {
  ensure_appimagetool
}

build_platform_installer() {
  local mode="$1"
  case "${mode}" in
    dmg)
      check_macos_prereqs
      ./scripts/build_dmg.sh
      ;;
    appimage)
      check_linux_prereqs
      ./scripts/build_appimage.sh
      ;;
    *)
      echo "error: unknown platform mode: ${mode}" >&2
      exit 1
      ;;
  esac
}

install_python_deps
compile_i18n
generate_icons
generate_manual
poe i18n-rcc
clean_pyinstaller_output
run_pyinstaller
verify_bundle_clean

if [[ "${PYINSTALLER_ONLY}" -eq 1 ]]; then
  echo "PyInstaller build complete (installer wrapper skipped)."
  exit 0
fi

if [[ "${PLATFORM_MODE}" == "auto" ]]; then
  PLATFORM_MODE="$(detect_platform_mode)"
fi

case "${PLATFORM_MODE}" in
  dmg)
    if [[ "$(uname -s)" != "Darwin" ]]; then
      echo "error: --dmg requires macOS" >&2
      exit 1
    fi
    ;;
  appimage)
    if [[ "$(uname -s)" != "Linux" ]]; then
      echo "error: --appimage requires Linux" >&2
      exit 1
    fi
    ;;
esac

build_platform_installer "${PLATFORM_MODE}"
echo "Build complete."
