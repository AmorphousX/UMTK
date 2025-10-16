# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_all

# Get the project root directory (two levels up from this spec file)
SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SPEC_DIR))

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
    (os.path.join(PROJECT_ROOT, 'style'), 'style'),
    (os.path.join(PROJECT_ROOT, 'img'), 'img'),
    (os.path.join(PROJECT_ROOT, 'lib/__init__.py'), 'lib'),
    (os.path.join(PROJECT_ROOT, 'lib/umtk_design.py'), 'lib'),
    (os.path.join(PROJECT_ROOT, 'lib/umtk_gui.py'), 'lib'), 
    (os.path.join(PROJECT_ROOT, 'lib/umtk_logic.py'), 'lib'),
    (os.path.join(PROJECT_ROOT, 'lib/UMTKSerial.py'), 'lib'),
    (os.path.join(PROJECT_ROOT, 'lib/theme_manager.py'), 'lib'),
    (os.path.join(PROJECT_ROOT, 'lib/record_dialog.py'), 'lib'),
    (os.path.join(PROJECT_ROOT, 'UMTK_Design_dynamic.ui'), '.'),
    (os.path.join(PROJECT_ROOT, 'UMTK_Design_preAI.ui'), '.'),
]

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
    [os.path.join(PROJECT_ROOT, 'main.py')],
    pathex=[PROJECT_ROOT],
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
    icon=os.path.join(PROJECT_ROOT, 'img/icon.ico') if os.path.exists(os.path.join(PROJECT_ROOT, 'img/icon.ico')) and sys.platform == 'win32' else None,
)