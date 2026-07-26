; Inno Setup script for Cash Flow Planner Desktop (Windows).
;
; Compile from the repository root:
;   iscc /DAppVersion=0.1.0 scripts\build_installer.iss
;
; Or set VERSION in the environment and pass it through CI:
;   iscc /DAppVersion=%VERSION% scripts\build_installer.iss
;
; After compilation, sign the installer in CI (when secrets are available):
;   signtool sign /f %WINDOWS_SIGN_CERT% /p %WINDOWS_SIGN_PASSWORD% ^
;     /tr http://timestamp.digicert.com /td sha256 /fd sha256 dist\cash-flow-planner-{#AppVersion}-win-setup.exe

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

#define AppName "Cash Flow Planner"
#define AppExeName "CashFlowPlanner.exe"
#define DistDir SourcePath + "\..\dist"
#define PyInstallerDist DistDir + "\CashFlowPlanner"
#define OutputBase "cash-flow-planner-" + AppVersion + "-win-setup"
#define AppIcon SourcePath + "\..\resources\icons\app-icon.ico"

[Setup]
AppId={{A3F8C2E1-9B4D-4F6A-8C1E-2D5E7F9A0B3C}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir={#DistDir}
OutputBaseFilename={#OutputBase}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile={#AppIcon}
UninstallDisplayIcon={app}\{#AppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#PyInstallerDist}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "*.db"

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
