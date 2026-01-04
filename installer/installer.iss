[Setup]
AppName=Smart File Wrangler
AppVersion=0.1.0
AppPublisher=ggvfx
DefaultDirName={autopf64}\SmartFileWrangler
DefaultGroupName=Smart File Wrangler
OutputBaseFilename=SmartFileWranglerInstaller
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
SetupIconFile=..\assets\smart-file-wrangler.ico
OutputDir=..\installer
ArchitecturesAllowed=x64compatible
UninstallFilesDir={app}
UninstallDisplayName=Uninstall Smart File Wrangler
UninstallDisplayIcon={app}\SmartFileWrangler.exe

[Files]
Source: "..\dist\SmartFileWrangler\SmartFileWrangler.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\SmartFileWrangler\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\src\smart_file_wrangler\main_window.ui"; DestDir: "{app}\_internal\smart_file_wrangler"; Flags: ignoreversion


[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"; Flags: checkedonce

[Icons]
Name: "{commondesktop}\Smart File Wrangler"; Filename: "{app}\SmartFileWrangler.exe"; IconFilename: "{app}\SmartFileWrangler.exe"; Tasks: desktopicon
Name: "{group}\Smart File Wrangler"; Filename: "{app}\SmartFileWrangler.exe"; IconFilename: "{app}\SmartFileWrangler.exe"; Tasks: desktopicon
Name: "{group}\Uninstall Smart File Wrangler"; Filename: "{uninstallexe}"

[Run]
; Optional FFmpeg install page link after install
Filename: "https://ffmpeg.org/download.html"; Description: "Download FFmpeg (optional)"; Flags: shellexec

