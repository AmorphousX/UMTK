# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_all
import sys

# Collect PyQt6 data and binaries with additional explicit Qt library collection
pyqt6_datas, pyqt6_binaries, pyqt6_hiddenimports = collect_all('PyQt6')

# Add explicit Qt library collection for macOS
if sys.platform == 'darwin':
    from PyInstaller.utils.hooks import collect_dynamic_libs
    # Explicitly collect Qt libraries to ensure they're included
    qt_binaries = collect_dynamic_libs('PyQt6.Qt6')
    pyqt6_binaries.extend(qt_binaries)

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

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,  # This tells PyInstaller it's onedir mode
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

# Create a COLLECT for onedir distribution
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False if sys.platform == 'darwin' else True,  # Disable UPX on macOS to avoid conflicts
    upx_exclude=[],
    name='umtk-ui'
)

# macOS-specific app bundle (disabled for onedir builds)
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