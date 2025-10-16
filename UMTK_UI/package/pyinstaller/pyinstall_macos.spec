# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_all

# Get the project root directory (two levels up from this spec file)
SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SPEC_DIR))

# Collect PyQt6 data and binaries with additional explicit Qt library collection
pyqt6_datas, pyqt6_binaries, pyqt6_hiddenimports = collect_all('PyQt6')

# Enhanced Qt library collection for macOS with robust fallback strategies
if sys.platform == 'darwin':
    from PyInstaller.utils.hooks import collect_dynamic_libs
    try:
        # Try to explicitly collect Qt libraries to ensure they're included
        qt_binaries = collect_dynamic_libs('PyQt6.Qt6')
        
        # Filter out duplicate frameworks to prevent symlink conflicts
        seen_frameworks = set()
        filtered_qt_binaries = []
        
        for binary_path, dest_path in qt_binaries:
            if '.framework' in binary_path:
                framework_name = os.path.basename(binary_path.split('.framework')[0] + '.framework')
                if framework_name not in seen_frameworks:
                    seen_frameworks.add(framework_name)
                    filtered_qt_binaries.append((binary_path, dest_path))
                else:
                    print(f"Skipping duplicate framework: {framework_name}")
            else:
                filtered_qt_binaries.append((binary_path, dest_path))
        
        pyqt6_binaries.extend(filtered_qt_binaries)
        print("Successfully collected PyQt6.Qt6 dynamic libs")
    except Exception as e:
        print(f"Warning: Could not collect PyQt6.Qt6 dynamic libs: {e}")
        # Try alternative collection approaches
        try:
            qt_binaries = collect_dynamic_libs('PyQt6')
            
            # Apply same filtering to fallback binaries
            seen_frameworks = set()
            filtered_qt_binaries = []
            
            for binary_path, dest_path in qt_binaries:
                if '.framework' in binary_path:
                    framework_name = os.path.basename(binary_path.split('.framework')[0] + '.framework')
                    if framework_name not in seen_frameworks:
                        seen_frameworks.add(framework_name)
                        filtered_qt_binaries.append((binary_path, dest_path))
                    else:
                        print(f"Skipping duplicate framework: {framework_name}")
                else:
                    filtered_qt_binaries.append((binary_path, dest_path))
            
            pyqt6_binaries.extend(filtered_qt_binaries)
            print("Successfully collected PyQt6 dynamic libs as fallback")
        except Exception as e2:
            print(f"Warning: Could not collect PyQt6 dynamic libs either: {e2}")
            # Add manual library paths if they exist
            import PyQt6
            pyqt6_path = os.path.dirname(PyQt6.__file__)
            possible_qt_paths = [
                os.path.join(pyqt6_path, 'Qt6', 'lib'),
                os.path.join(pyqt6_path, 'Qt', 'lib'),
                pyqt6_path
            ]
            for qt_path in possible_qt_paths:
                if os.path.exists(qt_path):
                    print(f"Found Qt path: {qt_path}")
                    # Add any .dylib files found in Qt paths
                    import glob
                    for dylib in glob.glob(os.path.join(qt_path, '*.dylib')):
                        pyqt6_binaries.append((dylib, '.'))
                    for framework in glob.glob(os.path.join(qt_path, '*.framework')):
                        pyqt6_binaries.append((framework, os.path.basename(framework)))

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
    # macOS-specific icon
    icon=os.path.join(PROJECT_ROOT, 'img/icon.icns') if os.path.exists(os.path.join(PROJECT_ROOT, 'img/icon.icns')) else None,
)

# Create a COLLECT for onedir distribution (macOS debugging mode)
# Clean up any problematic symlinks before creating COLLECT
import shutil
try:
    # Remove any existing dist directory to avoid symlink conflicts
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("Cleaned existing dist directory")
    
    # Also clean any cached framework files that might cause conflicts
    import tempfile
    temp_dir = tempfile.gettempdir()
    import glob
    for qt_framework_cache in glob.glob(os.path.join(temp_dir, '*Qt*.framework')):
        try:
            if os.path.islink(qt_framework_cache):
                os.unlink(qt_framework_cache)
            elif os.path.isdir(qt_framework_cache):
                shutil.rmtree(qt_framework_cache)
            print(f"Cleaned framework cache: {qt_framework_cache}")
        except Exception as e:
            print(f"Could not clean framework cache {qt_framework_cache}: {e}")
            
except Exception as e:
    print(f"Could not clean dist directory: {e}")

# More aggressive approach: Use PyInstaller's --onedir mode with manual framework handling
# Instead of letting PyInstaller handle framework symlinks, we'll force copy mode

# Override PyInstaller's symlink behavior for frameworks by patching the COLLECT process
import PyInstaller.building.api

# Store original symlink function
original_symlink = os.symlink

def safe_symlink(src, dst):
    """Custom symlink function that handles existing files/links"""
    try:
        # If destination exists, remove it first
        if os.path.exists(dst) or os.path.islink(dst):
            if os.path.isdir(dst) and not os.path.islink(dst):
                shutil.rmtree(dst)
            else:
                os.unlink(dst)
        
        # Create parent directory if it doesn't exist
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        
        # Create the symlink
        original_symlink(src, dst)
        print(f"Created symlink: {src} -> {dst}")
    except Exception as e:
        print(f"Failed to create symlink {src} -> {dst}: {e}")
        # Fallback: try to copy instead of symlink
        try:
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
            print(f"Copied instead of symlink: {src} -> {dst}")
        except Exception as e2:
            print(f"Failed to copy as fallback {src} -> {dst}: {e2}")

# Temporarily replace os.symlink with our safe version during COLLECT
os.symlink = safe_symlink

# Filter binaries again at collect time to remove any remaining duplicates
filtered_binaries = []
seen_frameworks = set()
seen_paths = set()

print("=== Filtering binaries to prevent symlink conflicts ===")
for i, binary in enumerate(a.binaries):
    # Binary tuple is typically (source_path, dest_name)
    if len(binary) >= 2:
        binary_path, dest_name = binary[0], binary[1]
    else:
        binary_path = binary[0]
        dest_name = ''
    
    # Create a unique identifier for this binary
    unique_id = f"{binary_path}|{dest_name}"
    
    if '.framework' in binary_path:
        # Extract the framework name from the path
        framework_parts = binary_path.split('.framework')
        if len(framework_parts) >= 2:
            framework_base = framework_parts[0].split('/')[-1]
            framework_name = f"{framework_base}.framework"
            
            # Also consider the specific file within the framework
            framework_file = framework_parts[1] if len(framework_parts) > 1 else ''
            framework_unique_id = f"{framework_name}{framework_file}"
            
            if framework_unique_id not in seen_frameworks and unique_id not in seen_paths:
                seen_frameworks.add(framework_unique_id)
                seen_paths.add(unique_id)
                filtered_binaries.append(binary)
                print(f"Including framework: {framework_name}{framework_file}")
            else:
                print(f"Excluding duplicate framework: {framework_name}{framework_file}")
        else:
            # Fallback for malformed framework paths
            if unique_id not in seen_paths:
                seen_paths.add(unique_id)
                filtered_binaries.append(binary)
    else:
        # For non-framework files, just check for path duplicates
        if unique_id not in seen_paths:
            seen_paths.add(unique_id)
            filtered_binaries.append(binary)

print(f"=== Filtered {len(a.binaries) - len(filtered_binaries)} duplicate binaries ===")

# Replace a.binaries with filtered version
a.binaries = filtered_binaries

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,  # Disable UPX on macOS to avoid conflicts
    upx_exclude=[],
    name='umtk-ui'
)

# Restore original symlink function
os.symlink = original_symlink
print("=== COLLECT completed successfully ===")

# macOS-specific app bundle (optional, disabled for debugging)
# Uncomment below if you want a .app bundle instead of directory executable
# app = BUNDLE(
#     exe,
#     name='UMTK-UI.app',
#     icon='img/icon.icns' if os.path.exists('img/icon.icns') else None,
#     bundle_identifier='com.umtk.ui',
#     info_plist={
#         'NSPrincipalClass': 'NSApplication',
#         'NSAppleScriptEnabled': False,
#         'CFBundleShortVersionString': '1.0.0',
#         'NSHighResolutionCapable': True,
#     },
# )