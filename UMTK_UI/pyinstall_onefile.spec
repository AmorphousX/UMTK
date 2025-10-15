# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_all

# Collect PyQt6 data and binaries
pyqt6_datas, pyqt6_binaries, pyqt6_hiddenimports = collect_all('PyQt6')

# Additional hidden imports - comprehensive PyQt6 modules
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.QtOpenGL',
    'PyQt6.sip',
    'sip',
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

# Create a single file executable (onefile mode)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
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
    # Platform-specific icon
    icon='img/icon.ico' if os.path.exists('img/icon.ico') and sys.platform == 'win32' else None,
)