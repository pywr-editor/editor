#define MyAppName "Pywr editor"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Stefano Simoncelli"
#define MyAppURL "https://github.com/pywr-editor/editor"
#define MyAppExeName "Pywr Editor.exe"
#define MyAppAssocName "JSON file"
#define MyAppAssocExt ".json"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{DEE7D1DF-6511-41D9-858A-DC477BBA2134}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableDirPage=yes
ChangesAssociations=yes
DisableProgramGroupPage=yes
LicenseFile=LICENSE.txt
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
OutputBaseFilename=Pywr editor installer
SetupIconFile=pywr_editor\assets\ico\Pywr Editor.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\main\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\_asyncio.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\_bz2.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\_ctypes.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\_decimal.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\_elementtree.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\_hashlib.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\_lzma.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\_multiprocessing.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\_overlapped.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\_queue.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\_socket.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\_ssl.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\_uuid.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\_win32sysloader.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-console-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-datetime-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-debug-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-errorhandling-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-fibers-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-file-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-file-l1-2-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-file-l2-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-handle-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-heap-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-interlocked-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-libraryloader-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-localization-l1-2-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-memory-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-namedpipe-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-processenvironment-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-processthreads-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-processthreads-l1-1-1.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-profile-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-rtlsupport-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-string-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-synch-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-synch-l1-2-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-sysinfo-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-timezone-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-util-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-winrt-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-core-winrt-string-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-crt-conio-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-crt-convert-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-crt-environment-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-crt-filesystem-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-crt-heap-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-crt-locale-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-crt-math-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-crt-multibyte-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-crt-process-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-crt-runtime-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-crt-stdio-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-crt-string-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-crt-time-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\api-ms-win-crt-utility-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\base_library.zip"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\LEGAL NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\libcrypto-1_1.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\libffi-7.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\libopenblas.FB5AE2TYXYH2IJRDKGDGQ3XBKLKTF43H.gfortran-win_amd64.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\libssl-1_1.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\mfc140u.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\pyexpat.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\python3.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\python310.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\Pywr Editor.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\Pywr Editor.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\select.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\ucrtbase.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\unicodedata.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\VCRUNTIME140.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\VCRUNTIME140_1.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\win32api.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\win32evtlog.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\win32pdh.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\win32trace.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\win32ui.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\markupsafe\*"; DestDir: "{app}\markupsafe"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\main\numexpr\*"; DestDir: "{app}\numexpr"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\main\numpy\*"; DestDir: "{app}\numpy"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\main\pandas\*"; DestDir: "{app}\pandas"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\main\PIL\*"; DestDir: "{app}\PIL"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\main\PySide6\*"; DestDir: "{app}\PySide6"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\main\pyqtgraph\*"; DestDir: "{app}\pyqtgraph"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\main\pytz\*"; DestDir: "{app}\pytz"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\main\pywin32_system32\*"; DestDir: "{app}\pywin32_system32"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\main\shiboken6\*"; DestDir: "{app}\shiboken6"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\main\tables\*"; DestDir: "{app}\tables"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\main\tables.libs\*"; DestDir: "{app}\tables.libs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\main\win32com\*"; DestDir: "{app}\win32com"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Registry]
;Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
;Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
;Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
;Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".myp"; ValueData: ""

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

