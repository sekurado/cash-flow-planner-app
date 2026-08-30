# One-command local build for Windows.
#
# Produces dist/cash-flow-planner-{version}-win-setup.exe
#
# Usage:
#   .\scripts\build.ps1
#   .\scripts\build.ps1 -Version 0.1.0
#   .\scripts\build.ps1 -PyInstallerOnly
#
# Prerequisites:
#   Python 3.12+, pip install -e ".[dev]", Inno Setup 6
[CmdletBinding()]
param(
    [string] $Version = "",
    [switch] $PyInstallerOnly
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root

function Get-ProjectVersion {
    param([string] $PyProjectPath)

    $content = Get-Content -Path $PyProjectPath -Raw
    if ($content -match '(?m)^version\s*=\s*"([^"]+)"') {
        return $Matches[1]
    }

    throw "Could not read version from $PyProjectPath"
}

function Require-Command {
    param(
        [string] $Name,
        [string] $Hint
    )

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name not found - $Hint"
    }
}

function Install-PythonDependencies {
    Require-Command python "install Python 3.12+"
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    python -m pip install -e .
    python -m pip install -e ".[ocr-windows]"
    python -m pip install pyinstaller pyinstaller-hooks-contrib
}

function Compile-I18n {
    Require-Command poe "run: pip install -e `".[dev]`""
    poe i18n-bundle
    if ($LASTEXITCODE -ne 0) {
        throw "poe i18n-bundle failed with exit code $LASTEXITCODE"
    }
}

function Generate-Icons {
    $env:QT_QPA_PLATFORM = "offscreen"
    python scripts/generate_app_icons.py
    if ($LASTEXITCODE -ne 0) {
        throw "generate_app_icons.py failed with exit code $LASTEXITCODE"
    }
}

function Generate-Manual {
    $env:QT_QPA_PLATFORM = "offscreen"
    python scripts/generate_manual.py --all
    if ($LASTEXITCODE -ne 0) {
        throw "generate_manual.py failed with exit code $LASTEXITCODE"
    }
}

function Invoke-I18nRcc {
    Require-Command poe "run: pip install -e `".[dev]`""
    poe i18n-rcc
    if ($LASTEXITCODE -ne 0) {
        throw "poe i18n-rcc failed with exit code $LASTEXITCODE"
    }
}

function Invoke-PyInstaller {
    pyinstaller cash_flow_planner.spec --noconfirm
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }
}

function Clear-PyInstallerOutput {
    $paths = @(
        (Join-Path $Root "build\CashFlowPlanner"),
        (Join-Path $Root "dist\CashFlowPlanner"),
        (Join-Path $Root "dist\CashFlowPlanner.app")
    )
    foreach ($path in $paths) {
        if (Test-Path $path) {
            Remove-Item -Recurse -Force $path
        }
    }
}

function Verify-BundleClean {
    $targets = @(
        (Join-Path $Root "dist\CashFlowPlanner"),
        (Join-Path $Root "dist\CashFlowPlanner.app")
    )
    python scripts/verify_bundle_clean.py @targets
    if ($LASTEXITCODE -ne 0) {
        throw "verify_bundle_clean failed with exit code $LASTEXITCODE"
    }
}

function Build-WindowsInstaller {
    param([string] $AppVersion)

    $pyInstallerDist = Join-Path $Root "dist\CashFlowPlanner"
    if (-not (Test-Path $pyInstallerDist)) {
        throw "PyInstaller output not found at $pyInstallerDist"
    }

    $iscc = Get-ChildItem -Path "${env:ProgramFiles(x86)}\Inno Setup 6" -Filter ISCC.exe `
        -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $iscc) {
        throw "ISCC.exe not found - install Inno Setup 6 from https://jrsoftware.org/isinfo.php or run: choco install innosetup"
    }

    & $iscc.FullName "/DAppVersion=$AppVersion" "scripts\build_installer.iss"
    if ($LASTEXITCODE -ne 0) {
        throw "ISCC failed with exit code $LASTEXITCODE"
    }
}

if ([string]::IsNullOrWhiteSpace($Version)) {
    $Version = Get-ProjectVersion -PyProjectPath (Join-Path $Root "pyproject.toml")
}

$env:VERSION = $Version
Write-Host "Building Cash Flow Planner $Version"

Install-PythonDependencies
Compile-I18n
Generate-Icons
Generate-Manual
Invoke-I18nRcc
Clear-PyInstallerOutput
Invoke-PyInstaller
Verify-BundleClean

if ($PyInstallerOnly) {
    Write-Host "PyInstaller build complete (installer wrapper skipped)."
    exit 0
}

Build-WindowsInstaller -AppVersion $Version
Write-Host "Build complete."
