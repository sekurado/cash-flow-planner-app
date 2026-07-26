#!/usr/bin/env bash
# Sign a PyInstaller-produced macOS .app bundle.
#
# Usage (source this file):
#   sign_macos_app_bundle /path/to/App.app [-|Developer ID Application: ...]
#
# Ad-hoc signing (-) is used for local / unsigned distribution.
# Developer ID signing requires entitlements and is intended for notarized releases.

sign_macos_app_bundle() {
  local app_path="$1"
  local identity="${2:--}"
  local entitlements="${3:-}"

  if [[ ! -d "${app_path}" ]]; then
    echo "error: app bundle not found: ${app_path}" >&2
    return 1
  fi

  local -a sign_args=(--force --sign "${identity}" --timestamp=none)
  local -a main_sign_args=(--force --sign "${identity}" --timestamp=none)

  if [[ "${identity}" != "-" ]]; then
    sign_args=(--force --sign "${identity}" --timestamp)
    main_sign_args=(
      --force
      --sign "${identity}"
      --timestamp
      --options
      runtime
    )
    if [[ -n "${entitlements}" ]]; then
      main_sign_args+=(--entitlements "${entitlements}")
    fi
  fi

  echo "Signing nested binaries in ${app_path}..."

  while IFS= read -r -d '' file; do
    codesign "${sign_args[@]}" "${file}"
  done < <(
    find "${app_path}/Contents" -type f \( -perm -111 -o -name "*.dylib" -o -name "*.so" \) \
      ! -path "*/_CodeSignature/*" -print0
  )

  echo "Signing app bundle ${app_path} with identity: ${identity}"
  codesign "${main_sign_args[@]}" "${app_path}"
  codesign --verify --deep --strict --verbose=2 "${app_path}"
}
