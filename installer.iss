[Setup]
AppName=YouTube Downloader
AppVersion=1.0
AppPublisher=TuNombre
DefaultDirName={pf}\YT_downloader
DefaultGroupName=YouTube Downloader
OutputDir=output
OutputBaseFilename=YouTubeDownloaderSetup
Compression=lzma
SolidCompression=yes
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\YouTubeDownloader.exe

[Files]
Source: "dist\YouTubeDownloader.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\YouTube Downloader"; Filename: "{app}\YouTubeDownloader.exe"
Name: "{commondesktop}\YouTube Downloader"; Filename: "{app}\YouTubeDownloader.exe"

[Run]
Filename: "{app}\YouTubeDownloader.exe"; Description: "Launch application"; Flags: postinstall nowait skipifsilent