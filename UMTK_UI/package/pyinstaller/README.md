# PyInstaller Package Directory

This directory contains all PyInstaller-related files for building the UMTK GUI application.

## Directory Structure

```
package/pyinstaller/
├── build.sh                    # Build script for all platforms
├── pyinstall.spec              # Default PyInstaller spec (cross-platform)
├── pyinstall_macos.spec        # macOS-optimized spec with framework handling
├── pyinstall_onefile.spec      # Single-file executable spec
└── README_macOS_Setup.txt       # User instructions for macOS quarantine removal
```

## Files Description

### Build Script
- **build.sh** - Universal build script that:
  - Auto-detects platform and selects appropriate spec file
  - Supports multiple build types (default, macos, onefile)
  - Activates virtual environment automatically
  - Cleans previous builds
  - Copies platform-specific documentation

### PyInstaller Spec Files
- **pyinstall.spec** - Default spec file for all platforms with Qt6 framework deduplication
- **pyinstall_macos.spec** - macOS-specific spec with advanced symlink conflict resolution
- **pyinstall_onefile.spec** - Creates single executable file (useful for Windows distribution)

### Documentation
- **README_macOS_Setup.txt** - Plain text instructions for macOS users to remove quarantine attributes

## Usage

### Quick Build (Auto-detect platform)
```bash
./package/pyinstaller/build.sh
```

### Platform-specific Builds
```bash
./package/pyinstaller/build.sh macos     # Force macOS spec
./package/pyinstaller/build.sh onefile   # Single file executable
./package/pyinstaller/build.sh default   # Cross-platform spec
```

### Manual PyInstaller Usage
```bash
# From project root directory
source guivenv/bin/activate
pyinstaller --clean --noconfirm package/pyinstaller/pyinstall_macos.spec
```

## Output

All builds create output in the project root `dist/` directory:
- **dist/umtk-ui/** - Application bundle directory
- **dist/README_macOS_Setup.txt** - Setup instructions (macOS builds only)

The GitHub Actions workflow packages this into zip files for distribution.

## Notes

- All spec files use relative paths from the project root
- The macOS spec includes advanced symlink conflict resolution
- Framework deduplication prevents Qt6 packaging issues
- Virtual environment must be set up before building