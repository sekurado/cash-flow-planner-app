#!/usr/bin/env bash
# Wrap a PyInstaller macOS .app bundle in a distributable .dmg.
#
# Prerequisites: pyinstaller cash_flow_planner.spec (produces dist/CashFlowPlanner.app)
#                brew install create-dmg  (or npm install -g create-dmg)
#
# Environment:
#   VERSION                      — optional, defaults to pyproject.toml version
#   OUTPUT_DIR                   — optional, defaults to dist/
#   APPLE_SIGN_IDENTITY          — Developer ID Application certificate name
#   APPLE_NOTARY_KEYCHAIN_PROFILE — notarytool keychain profile name
#
# Signing policy:
#   - Local / unsigned builds: ad-hoc sign (-) so Gatekeeper shows the standard
#     "unidentified developer" prompt (right-click → Open still works).
#   - Release builds: set BOTH APPLE_SIGN_IDENTITY and APPLE_NOTARY_KEYCHAIN_PROFILE.
#     Developer ID signing without notarization is intentionally skipped — it produces
#     worse Gatekeeper behaviour and can prevent Qt from launching.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck source=lib/build_version.sh
source "${ROOT}/scripts/lib/build_version.sh"
# shellcheck source=lib/codesign_macos_app.sh
source "${ROOT}/scripts/lib/codesign_macos_app.sh"
ensure_version

OUTPUT_DIR="${OUTPUT_DIR:-dist}"
APP_PATH="dist/CashFlowPlanner.app"
DMG_NAME="cash-flow-planner-${VERSION}-mac.dmg"
DMG_PATH="${OUTPUT_DIR}/${DMG_NAME}"
ENTITLEMENTS_PATH="${ROOT}/scripts/macos/entitlements.plist"

if [[ ! -d "$APP_PATH" ]]; then
  echo "error: ${APP_PATH} not found — run 'pyinstaller cash_flow_planner.spec' first" >&2
  exit 1
fi

if ! command -v create-dmg >/dev/null 2>&1; then
  echo "error: create-dmg not found — install via 'brew install create-dmg'" >&2
  exit 1
fi

if [[ -n "${APPLE_NOTARY_KEYCHAIN_PROFILE:-}" && -z "${APPLE_SIGN_IDENTITY:-}" ]]; then
  echo "error: APPLE_NOTARY_KEYCHAIN_PROFILE requires APPLE_SIGN_IDENTITY" >&2
  exit 1
fi

if [[ -n "${APPLE_SIGN_IDENTITY:-}" && -n "${APPLE_NOTARY_KEYCHAIN_PROFILE:-}" ]]; then
  if [[ ! -f "${ENTITLEMENTS_PATH}" ]]; then
    echo "error: entitlements file not found: ${ENTITLEMENTS_PATH}" >&2
    exit 1
  fi
  sign_macos_app_bundle "${APP_PATH}" "${APPLE_SIGN_IDENTITY}" "${ENTITLEMENTS_PATH}"
elif [[ -n "${APPLE_SIGN_IDENTITY:-}" ]]; then
  echo "warning: APPLE_SIGN_IDENTITY is set without APPLE_NOTARY_KEYCHAIN_PROFILE;" >&2
  echo "warning: using ad-hoc signing instead (Developer ID without notarization breaks Gatekeeper)." >&2
  sign_macos_app_bundle "${APP_PATH}" "-"
else
  sign_macos_app_bundle "${APP_PATH}" "-"
fi

if [[ -n "${APPLE_NOTARY_KEYCHAIN_PROFILE:-}" ]]; then
  echo "Submitting ${APP_PATH} for notarization..."
  xcrun notarytool submit "${APP_PATH}" \
    --keychain-profile "${APPLE_NOTARY_KEYCHAIN_PROFILE}" \
    --wait
  xcrun stapler staple "${APP_PATH}"
  xcrun stapler validate "${APP_PATH}"
fi

mkdir -p "${OUTPUT_DIR}"
rm -f "${DMG_PATH}"

ICON_PATH="${ROOT}/resources/icons/app-icon.icns"
CREATE_DMG_ARGS=(
  --volname "Cash Flow Planner"
  --app-drop-link 600 185
)
if [[ -f "${ICON_PATH}" ]]; then
  CREATE_DMG_ARGS+=(--volicon "${ICON_PATH}")
fi

create-dmg \
  "${CREATE_DMG_ARGS[@]}" \
  "${DMG_PATH}" \
  "${APP_PATH}"

if [[ -n "${APPLE_NOTARY_KEYCHAIN_PROFILE:-}" ]]; then
  echo "Submitting ${DMG_PATH} for notarization..."
  xcrun notarytool submit "${DMG_PATH}" \
    --keychain-profile "${APPLE_NOTARY_KEYCHAIN_PROFILE}" \
    --wait
  xcrun stapler staple "${DMG_PATH}"
  xcrun stapler validate "${DMG_PATH}"
  echo "Notarization complete."
fi

echo "Created ${DMG_PATH}"
