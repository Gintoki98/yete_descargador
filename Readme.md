App para descargar videos de Y T
Instrucciones de uso:
Puede correr el script directamente o compilando un ejecutable (y luego creando un instalador para distribuir)

En la interfaz, pegue el enlace que quiere descargar.
Seleccione la ruta donde desee guardar la descarga.
Pulse Get Formats para solicitar todas las resoluciones disponibles.
Seleccione la resolución deseada (si hace scroll hacia abajo en la lista puede encontrar las pistas de audio).
Pulse Download y espere a que termine la descarga.

Listo, ya puede disfrutar de su descarga localmente

Instrucciones para compilar y empaquetar en un instalador su app:

### 1. Instalar herramientas necesarias
```bash
pip install pyinstaller
```

### 2. Crear un archivo .spec para PyInstaller
Crea un archivo `youtube_downloader.spec` con este contenido (ajusta los nombres y rutas):

```python
# -*- mode: python -*-
import sys  # <-- Añade esta línea al inicio
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.config import CONF
CONF['workpath'] = CONF['workpath'] + "_win7"

block_cipher = None

def get_ffmpeg_binaries():
    if sys.platform == 'win32':
        return [('ffmpeg.exe', '.')]
    return []

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=get_ffmpeg_binaries(),
    datas=collect_data_files('yt_dlp') + [('icon.ico', '.')],
    hiddenimports=[
        'yt_dlp',
        'tkinter',
        'PIL',
        'pkg_resources.py2_warn'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['test'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YouTubeDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='icon.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True
)
```

### 3. Compilar con PyInstaller
```bash
pyinstaller youtube_downloader.spec --onefile --windowed
```

### 4. Crear instalador con Inno Setup
1. Descarga Inno Setup: https://jrsoftware.org/isinfo.php
2. Crea un script `installer.iss`:

```iss
[Setup]
AppName=YeTe Downloader
AppVersion=1.0
AppPublisher=TuNombre
DefaultDirName={pf}\YT_downloader
DefaultGroupName=YeTe Downloader
OutputDir=output
OutputBaseFilename=YeTeDownloaderSetup
Compression=lzma
SolidCompression=yes
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\YouTubeDownloader.exe

[Files]
Source: "dist\YeTeDownloader.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\YeTe Downloader"; Filename: "{app}\YeTeDownloader.exe"
Name: "{commondesktop}\YeTe Downloader"; Filename: "{app}\YeTeDownloader.exe"

[Run]
Filename: "{app}\YeTeDownloader.exe"; Description: "Launch application"; Flags: postinstall nowait skipifsilent
```

### 5. Pasos adicionales importantes
1. **Incluir FFmpeg** (para combinar audio/video):
   - Descarga ffmpeg.exe desde https://ffmpeg.org/
   - Añádelo al .spec en la sección `binaries`:
     ```python
     binaries=[('ffmpeg.exe', '.')],
     ```

2. **Si la aplicación se cierra inesperadamente**:
   - Compila con `console=True` temporalmente para ver errores
   - Agrega try/except en tu código para registrar errores en un archivo log

