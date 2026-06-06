; USBIP-WSL-Manager 安装脚本

[Setup]
AppName=USBIP-WSL-Manager
AppVersion=1.0
AppPublisher=USBIP-WSL
DefaultDirName={autopf}\USBIP-WSL-Manager
DefaultGroupName=USBIP-WSL-Manager
OutputDir=.\installer
OutputBaseFilename=USBIP-WSL-Manager-Setup
SetupIconFile=icon.svg
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "dist\USBIP-WSL-Manager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.svg"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\USBIP-WSL-Manager"; Filename: "{app}\USBIP-WSL-Manager.exe"; WorkingDir: "{app}"
Name: "{group}\卸载 USBIP-WSL-Manager"; Filename: "{uninstallexe}"
Name: "{commondesktop}\USBIP-WSL-Manager"; Filename: "{app}\USBIP-WSL-Manager.exe"; WorkingDir: "{app}"

[Run]
Filename: "{app}\USBIP-WSL-Manager.exe"; Description: "启动 USBIP-WSL-Manager"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
