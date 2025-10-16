#!/bin/bash

# UMTK GUI PyInstaller Build Script
# This script builds the UMTK GUI application using PyInstaller

set -e  # Exit on any error

echo "=========================================="
echo "UMTK GUI PyInstaller Build Script"
echo "=========================================="

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUILD_TYPE="${1:-default}"

# Show help if requested
if [[ "$BUILD_TYPE" == "--help" ]] || [[ "$BUILD_TYPE" == "-h" ]] || [[ "$BUILD_TYPE" == "help" ]]; then
    echo "Usage: $0 [BUILD_TYPE]"
    echo ""
    echo "Build types:"
    echo "  default   - Auto-detect platform (macOS uses app bundle, others use onedir)"
    echo "  onefile   - Create single executable file"
    echo "  macos     - Create macOS app bundle (macOS only)"
    echo "  darwin    - Same as macos"
    echo ""
    echo "Examples:"
    echo "  $0              # Auto-detect platform"
    echo "  $0 onefile      # Create single executable"
    echo "  $0 macos        # Create macOS app bundle"
    echo ""
    exit 0
fi

echo "Script directory: $SCRIPT_DIR"
echo "Project root: $PROJECT_ROOT"
echo "Build type: $BUILD_TYPE"

# Change to project root
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "guivenv" ]; then
    echo "Error: Virtual environment 'guivenv' not found in $PROJECT_ROOT"
    echo "Please create the virtual environment first:"
    echo "  python3 -m venv guivenv"
    echo "  source guivenv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source guivenv/bin/activate

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "Error: PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist
rm -rf ~/.pyinstaller_cache 2>/dev/null || true

# Detect platform and select appropriate spec file
SPEC_FILE=""
PLATFORM=$(uname)

case "$BUILD_TYPE" in
    "onefile")
        SPEC_FILE="package/pyinstaller/pyinstall_onefile.spec"
        echo "Building onefile executable..."
        ;;
    "macos"|"darwin")
        SPEC_FILE="package/pyinstaller/pyinstall_macos.spec"
        echo "Building macOS bundle..."
        ;;
    "default"|*)
        if [[ "$PLATFORM" == "Darwin" ]]; then
            SPEC_FILE="package/pyinstaller/pyinstall_macos.spec"
            echo "Auto-detected macOS, using macOS spec..."
        else
            SPEC_FILE="package/pyinstaller/pyinstall.spec"
            echo "Using default spec file..."
        fi
        ;;
esac

echo "Using spec file: $SPEC_FILE"

# Check if spec file exists
if [ ! -f "$SPEC_FILE" ]; then
    echo "Error: Spec file not found: $SPEC_FILE"
    exit 1
fi

# Run PyInstaller
echo "Running PyInstaller..."
pyinstaller --clean --noconfirm "$SPEC_FILE"

# Check if build was successful
if [ -d "dist" ]; then
    echo "=========================================="
    echo "Build completed successfully!"
    echo "=========================================="
    echo "Output directory: $PROJECT_ROOT/dist"
    ls -la dist/
    
    # Copy platform-specific README if it exists
    if [[ "$PLATFORM" == "Darwin" ]] && [ -f "package/pyinstaller/README_macOS_Setup.txt" ]; then
        echo "Copying macOS setup instructions..."
        cp package/pyinstaller/README_macOS_Setup.txt dist/
    fi
    
else
    echo "=========================================="
    echo "Build failed!"
    echo "=========================================="
    exit 1
fi

echo "Build script completed."