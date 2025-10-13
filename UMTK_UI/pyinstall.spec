# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_all

# Collect all PyQt6 data and binaries
pyqt6_datas, pyqt6_binaries, pyqt6_hiddenimports = collect_all('PyQt6')

# Additional hidden imports
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.QtOpenGL',
    'matplotlib.backends.backend_qt5agg',
    'matplotlib.backends.backend_qtagg',
    'serial',
    'serial.tools',
    'serial.tools.list_ports',
    'numpy',
    'pandas'
] + pyqt6_hiddenimports

# Data files to include
datas = [
    ('img', 'img'),
    ('style', 'style'), 
    ('lib', 'lib'),
] + pyqt6_datas

# Filter out any non-existent paths
filtered_datas = []
for src, dst in datas:
    if os.path.exists(src):
        filtered_datas.append((src, dst))
        print(f"Including: {src} -> {dst}")
    elif '*' in src:
        # Handle glob patterns like *.ui
        import glob
        for file in glob.glob(src):
            if os.path.exists(file):
                filtered_datas.append((file, dst))
                print(f"Including: {file} -> {dst}")
    else:
        print(f"Warning: Path does not exist: {src}")

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=pyqt6_binaries,
    datas=filtered_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,        # Include binaries in the executable (onefile mode)
    a.zipfiles,        # Include zipfiles in the executable (onefile mode)
    a.datas,           # Include data files in the executable (onefile mode)
    [],
    name='umtk-ui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,  # Use system default temp directory
    console=False,  # Set to False for windowed mode (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Windows-specific icon (optional)
    icon='img/icon.ico' if os.path.exists('img/icon.ico') else None,
)

# macOS-specific app bundle (disabled for onefile builds)
# Uncomment below if you want a .app bundle instead of single executable
# if sys.platform == 'darwin':
#     app = BUNDLE(
#         exe,
#         name='UMTK-UI.app',
#         icon='img/icon.icns' if os.path.exists('img/icon.icns') else None,
#         bundle_identifier='com.umtk.ui',
#         info_plist={
#             'NSPrincipalClass': 'NSApplication',
#             'NSAppleScriptEnabled': False,
#             'CFBundleShortVersionString': '1.0.0',
#             'NSHighResolutionCapable': True,
#         },
#     )