#define AppName "PyNivo"
#define AppVersion "0.1.0"
#define AppPublisher "PyNivo Project"
#define AppExeName "PyNivo.exe"

[Setup]
AppId={{D8D84751-8B26-4EB6-9709-D62020DD9455}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion} Preview
AppPublisher={#AppPublisher}
AppPublisherURL=https://github.com/asadabbas717/pynivo
AppSupportURL=https://github.com/asadabbas717/pynivo/issues
AppUpdatesURL=https://github.com/asadabbas717/pynivo/releases
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=..\..\dist\installer
OutputBaseFilename=PyNivo-{#AppVersion}-Preview-Setup-x64
SetupIconFile=..\..\resources\branding\pynivo.ico
LicenseFile=..\..\build\installer-license.txt
UninstallDisplayIcon={app}\{#AppExeName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no
SetupLogging=yes
VersionInfoVersion={#AppVersion}.0
VersionInfoProductName={#AppName}
VersionInfoDescription={#AppName} preview installer

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "..\..\dist\PyNivo\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Parameters: "--welcome"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
