#!/usr/bin/env bash
# Wrap PyInstaller onedir output in a Linux AppImage.
#
# Prerequisites:
#   pyinstaller cash_flow_planner.spec   (produces dist/CashFlowPlanner/)
#   appimagetool                         (download from GitHub AppImage/AppImageKit releases)
#
# Environment:
#   VERSION       — optional, defaults to pyproject.toml version
#   OUTPUT_DIR    — optional, defaults to dist/
#   APPIMAGETOOL  — optional path to appimagetool binary
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck source=lib/build_version.sh
source "${ROOT}/scripts/lib/build_version.sh"
ensure_version

OUTPUT_DIR="${OUTPUT_DIR:-dist}"
APPIMAGE_NAME="cash-flow-planner-${VERSION}-linux.AppImage"
APPIMAGE_PATH="${OUTPUT_DIR}/${APPIMAGE_NAME}"
APPDIR="${ROOT}/build/AppDir"
PYINSTALLER_DIST="${ROOT}/dist/CashFlowPlanner"
APPIMAGETOOL="${APPIMAGETOOL:-appimagetool}"

if [[ ! -d "${PYINSTALLER_DIST}" ]]; then
  echo "error: ${PYINSTALLER_DIST} not found — run 'pyinstaller cash_flow_planner.spec' first" >&2
  exit 1
fi

if ! command -v "${APPIMAGETOOL}" >/dev/null 2>&1 && [[ ! -x "${APPIMAGETOOL}" ]]; then
  echo "error: ${APPIMAGETOOL} not found — set APPIMAGETOOL or install appimagetool" >&2
  exit 1
fi

rm -rf "${APPDIR}"
mkdir -p "${APPDIR}/usr/lib/CashFlowPlanner"
mkdir -p "${APPDIR}/usr/share/applications"

cp -a "${PYINSTALLER_DIST}/." "${APPDIR}/usr/lib/CashFlowPlanner/"

cat > "${APPDIR}/AppRun" << 'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0" 2>/dev/null || realpath "$0")")"
cd "${HERE}/usr/lib/CashFlowPlanner"
exec "${HERE}/usr/lib/CashFlowPlanner/CashFlowPlanner" "$@"
EOF
chmod +x "${APPDIR}/AppRun"

cat > "${APPDIR}/cash-flow-planner.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Cash Flow Planner
Comment=Offline-first cash flow forecasting
Exec=CashFlowPlanner
Icon=cash-flow-planner
Categories=Office;Finance;
Terminal=false
StartupWMClass=CashFlowPlanner
EOF

cp "${APPDIR}/cash-flow-planner.desktop" "${APPDIR}/usr/share/applications/"

ICON_SRC="${ROOT}/resources/icons/app-icon.svg"
if [[ ! -f "${ICON_SRC}" ]]; then
  echo "error: ${ICON_SRC} not found — required for AppImage desktop integration" >&2
  exit 1
fi
cp "${ICON_SRC}" "${APPDIR}/cash-flow-planner.svg"

mkdir -p "${OUTPUT_DIR}"
rm -f "${APPIMAGE_PATH}"

ARCH="${ARCH:-$(uname -m)}"
export ARCH

is_appimage_tool() {
  [[ "${APPIMAGETOOL}" == *.AppImage ]] && return 0
  file -b "${APPIMAGETOOL}" 2>/dev/null | grep -qi 'appimage'
}

run_appimagetool() {
  # CI runners and minimal containers often lack libfuse2; extract-and-run avoids FUSE.
  if is_appimage_tool; then
    APPIMAGE_EXTRACT_AND_RUN=1 "${APPIMAGETOOL}" "$@"
  else
    "${APPIMAGETOOL}" "$@"
  fi
}

run_appimagetool --no-appstream "${APPDIR}" "${APPIMAGE_PATH}"
chmod +x "${APPIMAGE_PATH}"

echo "Created ${APPIMAGE_PATH}"
