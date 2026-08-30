# Building Installers Locally

This guide explains how to produce distributable installers on your own machine
so you can share them with friends and family. Each platform must be built on
that platform — PyInstaller cannot cross-compile.

| Platform | Command | Output |
|----------|---------|--------|
| macOS | `./scripts/build.sh` | `dist/cash-flow-planner-{version}-mac.dmg` |
| Windows | `.\scripts\build.ps1` | `dist/cash-flow-planner-{version}-win-setup.exe` |
| Linux | `./scripts/build.sh` | `dist/cash-flow-planner-{version}-linux.AppImage` |

The version is read from `pyproject.toml` by default. Override with `VERSION=0.2.0`
(macOS/Linux) or `.\scripts\build.ps1 -Version 0.2.0` (Windows).

---

## Prerequisites

### All platforms

- **Python 3.12+**
- A virtual environment is recommended but not required
- Dev dependencies (for `poe i18n-bundle`):

  ```bash
  pip install -e ".[dev]"
  ```

### macOS

- Xcode Command Line Tools (`xcode-select --install`)
- [create-dmg](https://github.com/create-dmg/create-dmg):

  ```bash
  brew install create-dmg
  ```

### Windows

- [Inno Setup 6](https://jrsoftware.org/isinfo.php) (installs `ISCC.exe`)
- Or via Chocolatey: `choco install innosetup`

### Linux

Install Qt runtime libraries required by PyInstaller (Ubuntu/Debian example):

```bash
sudo apt-get update
sudo apt-get install -y \
  libegl1 libglib2.0-0 libxkbcommon-x11-0 libxcb-cursor0 \
  libdbus-1-3 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
  libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-xfixes0 \
  libxcb-xinerama0 libxcb-xkb1 libxkbcommon0
```

`appimagetool` is downloaded automatically by `build.sh` into `build/tools/` when
not already on your `PATH`.

### Optional receipt OCR (macOS Vision)

On-device receipt scanning uses the **macOS Vision** framework (`VNRecognizeTextRequest`)
through PyObjC. It is **not** a core dependency: Linux, Windows, and CI stay installable
without it. Core spending entry stays fully offline (NFR-01).

| Platform | Native OCR in v1 | What to install |
|----------|------------------|-----------------|
| macOS | Vision via `MacosVisionOcrProvider` | `pip install -e ".[ocr-macos]"` (needs Xcode Command Line Tools) |
| Windows | Stub — Scan shows a manual-entry error | Nothing extra |
| Linux | Stub — do **not** bundle Tesseract | Nothing extra |

**Source runs on macOS**

```bash
pip install -e ".[dev,ocr-macos]"
```

If PyObjC is missing, Scan still opens the form: the ViewModel surfaces
`ReceiptOcrUnavailableError` and the user can type the expense.

**PyInstaller / installer builds**

- `MacosVisionOcrProvider` **lazy-imports** `Vision` and `Foundation`, so Linux/Windows
  freezes never pull macOS-only frameworks.
- `cash_flow_planner.spec` adds `Vision`, `Foundation`, and `objc` to `hiddenimports`
  **only on macOS** and only when those modules are importable at freeze time.
- `./scripts/build.sh` installs the `ocr-macos` extra on Darwin so a local macOS DMG
  can ship working Scan. Windows (`build.ps1`) and Linux do not install that extra.
- Cloud document APIs are a Settings stub (`receipt_ocr_cloud_enabled`, default off).
  They add no freeze-time binaries and do not upload receipt photos.

See [receipt-ocr.md](./receipt-ocr.md) for the provider contract and accuracy notes.

---

## One-command build

### macOS

```bash
pip install -e ".[dev]"
./scripts/build.sh
```

Open the resulting `.dmg`, drag **CashFlowPlanner** to Applications, and launch Cash Flow Planner.

### Windows

```powershell
pip install -e ".[dev]"
.\scripts\build.ps1
```

Run the `.exe` installer and follow the wizard.

### Linux

```bash
pip install -e ".[dev]"
./scripts/build.sh
chmod +x dist/cash-flow-planner-*-linux.AppImage
./dist/cash-flow-planner-*-linux.AppImage
```

The AppImage works on both apt-based (Ubuntu, Debian) and rpm-based (Fedora, RHEL)
distributions without root access.

---

## Build options

### macOS / Linux (`build.sh`)

| Flag | Description |
|------|-------------|
| `--dmg` | Build macOS `.dmg` only (requires macOS) |
| `--appimage` | Build Linux AppImage only (requires Linux) |
| `--pyinstaller-only` | Skip installer wrapper; output PyInstaller bundle only |

### Windows (`build.ps1`)

| Flag | Description |
|------|-------------|
| `-Version 0.1.0` | Override version string |
| `-PyInstallerOnly` | Skip Inno Setup; output PyInstaller bundle only |

### Poe shortcuts

```bash
poe build              # macOS/Linux only (runs build.sh)
poe build-pyinstaller  # PyInstaller bundle on any platform
```

On Windows, use `.\scripts\build.ps1` directly instead of `poe build`.

---

## What gets built

After a full build, `dist/` contains:

```
dist/
  CashFlowPlanner/                 # PyInstaller onedir (intermediate)
  CashFlowPlanner.app              # macOS only (intermediate)
  cash-flow-planner-0.1.0-mac.dmg
  cash-flow-planner-0.1.0-win-setup.exe
  cash-flow-planner-0.1.0-linux.AppImage
```

Share the single installer file for each platform. Recipients do **not** need
Python installed.

---

## Sharing unsigned builds with friends and family

Local builds are not code-signed by default. Operating systems will show security
warnings — this is expected for personal distribution.

### macOS (Gatekeeper)

The first launch may show *"CashFlowPlanner cannot be opened because it is from
an unidentified developer."*

**Workaround:** Right-click the app → **Open** → confirm **Open**. Alternatively,
go to **System Settings → Privacy & Security** and click **Open Anyway**.

If macOS only offers to allow the app from **System Settings** (no **Open** button
in the dialog), the build was likely **signed but not notarized** — for example
`APPLE_SIGN_IDENTITY` was set without `APPLE_NOTARY_KEYCHAIN_PROFILE`. Rebuild
without `APPLE_SIGN_IDENTITY`, or configure both variables for a notarized release.

After downloading a DMG from the internet, remove the quarantine flag before the
first launch if the app appears to hang with no window:

```bash
xattr -cr /Applications/CashFlowPlanner.app
```

### Windows (SmartScreen)

The installer may show *"Windows protected your PC"* with an unknown publisher.

**Workaround:** Click **More info** → **Run anyway**.

### Linux (AppImage)

1. Make the file executable: `chmod +x cash-flow-planner-*-linux.AppImage`
2. Double-click or run from a terminal: `./cash-flow-planner-*-linux.AppImage`

On older distributions without FUSE2, run with:

```bash
APPIMAGE_EXTRACT_AND_RUN=1 ./cash-flow-planner-*-linux.AppImage
```

---

## Optional code signing

For wider distribution without security warnings, you can sign builds when you have
certificates:

| Platform | Environment variables |
|----------|----------------------|
| macOS | `APPLE_SIGN_IDENTITY`, `APPLE_NOTARY_KEYCHAIN_PROFILE`, `APPLE_CERTIFICATE_P12` (base64), `APPLE_CERTIFICATE_PASSWORD`, `APPLE_ID`, `APPLE_TEAM_ID`, `APPLE_APP_SPECIFIC_PASSWORD` |
| Windows | Sign with `signtool` after build (see `scripts/build_installer.iss` header comment) |

For GitHub Actions release builds, configure **all** macOS secrets above. The workflow imports the
Developer ID certificate into a temporary keychain and registers the notarytool profile on each run.
If only `APPLE_SIGN_IDENTITY` is set without the notary credentials, the build script falls back to
ad-hoc signing (right-click → **Open** works; avoid distributing signed-but-not-notarized builds).

---

## User manual PDF

Regenerate bundled user-manual PDFs for every supported locale before release builds:

```bash
python scripts/generate_manual.py --all
poe i18n-rcc
```

Use `--locale en` (or `fr`, `ru`, `es`, `de`) to rebuild a single language during development.

`scripts/build.sh` and `scripts/build.ps1` run `generate_manual.py --all` and refresh the Qt
resource bundle automatically before PyInstaller.

---

## Smoke test after building

1. Launch the installed app.
2. Create a new plan and add an entry.
3. Run a simulation and confirm the balance chart renders.
4. Quit and relaunch — data should persist in the OS app-data directory:
   - macOS: `~/Library/Application Support/CashFlowPlanner/CashFlowPlannerDesktop/`
   - Windows: `%LOCALAPPDATA%\CashFlowPlanner\CashFlowPlannerDesktop\`
   - Linux: `~/.local/share/CashFlowPlanner/CashFlowPlannerDesktop/`

Upgrading from a **Financial Tracker** install migrates settings and the database
automatically on first launch. Legacy data remains under the old `FinancialTracker`
path until removed manually.

---

## Clean install verification

Before sharing an installer, confirm that no user database leaked into the build
artifacts. The unified build scripts (`build.sh`, `build.ps1`) run
`scripts/verify_bundle_clean.py` automatically after PyInstaller; CI fails the
build job if any `*.db` file is found.

### Scan PyInstaller output manually

```bash
# macOS / Linux
find dist/CashFlowPlanner dist/CashFlowPlanner.app -name '*.db' 2>/dev/null

# Windows (PowerShell)
Get-ChildItem -Recurse dist\CashFlowPlanner -Filter *.db
```

Both commands should produce **no output**.

### Scan the Windows installer (optional)

Extract the Inno Setup payload with [7-Zip](https://www.7-zip.org/) or inspect the
`iscc` log and confirm no `cash_flow_planner.db` or `financial_tracker.db` is listed
under `{app}`.

### Verify first launch on a clean profile

On a machine or VM that has **never** run Cash Flow Planner (or the legacy Financial
Tracker app):

1. Install from the built installer.
2. Launch the app — the forecast list must be **empty**.
3. Confirm the database file is created only under the AppData path (not next to the
   executable):
   - Windows: `%LOCALAPPDATA%\CashFlowPlanner\CashFlowPlannerDesktop\cash_flow_planner.db`
   - macOS: `~/Library/Application Support/CashFlowPlanner/CashFlowPlannerDesktop/cash_flow_planner.db`
   - Linux: `~/.local/share/CashFlowPlanner/CashFlowPlannerDesktop/cash_flow_planner.db`

If a forecast such as "Plan1" appears on first launch, a stale database was likely
packaged into `dist/CashFlowPlanner/` before the installer step. Re-run the build
after `Clear-PyInstallerOutput` / `clean_pyinstaller_output` removes stale artifacts.

---

## Repository naming (maintainers)

| Artifact | Canonical name |
|----------|----------------|
| GitHub repository | `cash-flow-planner-app` |
| Python package (`pyproject.toml`) | `cash-flow-planner-desktop` |
| Release installer artifacts | `cash-flow-planner-{version}-*` |

Legacy checkouts or remotes may still reference `financial-tracker-desktop`; update
with `git remote set-url origin git@github.com:<org>/cash-flow-planner-app.git`.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| App hangs on launch, no window (downloaded DMG) | `xattr -cr /Applications/CashFlowPlanner.app`, then right-click → **Open**; if still stuck, upgrade to a build that includes the macOS window-activation fix |
| Gatekeeper only allows override in System Settings | Rebuild without `APPLE_SIGN_IDENTITY`, or configure full notarization secrets (see table above) |
| `create-dmg not found` | `brew install create-dmg` |
| `ISCC.exe not found` | Install [Inno Setup 6](https://jrsoftware.org/isinfo.php) |
| `poe: command not found` | `pip install -e ".[dev]"` |
| PyInstaller fails on Linux with missing `.so` | Install the apt packages listed above |
| AppImage won't run | `chmod +x` the file; try `APPIMAGE_EXTRACT_AND_RUN=1` |

For the CI release pipeline (GitHub Actions), see [DESIGN.md §16](./DESIGN.md#16-build-and-release-pipeline).

On every push and pull request to `main`, CI runs lint and tests only. Installer builds
run on semver tag pushes such as `1.0.0`, when a version bump on `main` auto-creates that tag
after E2E passes, or via manual **workflow_dispatch** with a release tag. They publish
the macOS `.dmg`, Windows `.exe`, and Linux `.AppImage` to GitHub Releases. Optional macOS signing/notarization uses repository secrets
`APPLE_SIGN_IDENTITY` and `APPLE_NOTARY_KEYCHAIN_PROFILE`.
