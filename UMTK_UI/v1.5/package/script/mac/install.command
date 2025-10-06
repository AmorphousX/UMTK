#!/bin/bash

# Store the current directory
current_dir=$(pwd)

# Ensure the script is executable
chmod +x "$0"

# Change to the directory where the script is located
cd "$(dirname "$0")"

echo "=== UMTK UI Installation for macOS ==="
echo ""

# Detect and display architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    echo "Detected: Apple Silicon Mac (arm64)"
    echo "Make sure you downloaded: umtk-ui-macos-arm64.zip"
elif [[ "$ARCH" == "x86_64" ]]; then
    echo "Detected: Intel Mac (x86_64)"
    echo "Make sure you downloaded: umtk-ui-macos-intel.zip"
else
    echo "Detected: Unknown architecture ($ARCH)"
fi
echo ""

# Handle Gatekeeper and quarantine issues for unsigned apps
echo "Checking for quarantine attributes (Gatekeeper)..."
if xattr -l . 2>/dev/null | grep -q "com.apple.quarantine"; then
    echo "Quarantine attribute detected. Removing to allow execution..."
    xattr -dr com.apple.quarantine . 2>/dev/null || true
    echo "Quarantine removed. App should now run without Gatekeeper warnings."
fi

# Make all scripts executable
chmod +x *.command 2>/dev/null || true
chmod +x *.sh 2>/dev/null || true

# If PyInstaller binary exists, remove quarantine from it too
if [ -f "umtk-ui" ]; then
    echo "Removing quarantine from umtk-ui binary..."
    xattr -dr com.apple.quarantine umtk-ui 2>/dev/null || true
    chmod +x umtk-ui
fi

echo ""
echo "=== Python Environment Setup ==="

# Function to check if Python version is compatible (3.8+)
check_python_version() {
    local python_cmd="$1"
    if command -v "$python_cmd" &> /dev/null; then
        version=$($python_cmd --version 2>&1 | awk '{print $2}')
        major=$(echo $version | cut -d. -f1)
        minor=$(echo $version | cut -d. -f2)
        
        if [[ $major -eq 3 ]] && [[ $minor -ge 8 ]]; then
            echo "Found compatible Python: $python_cmd $version"
            PYTHON_CMD="$python_cmd"
            return 0
        fi
    fi
    return 1
}

# Try to find a suitable Python version
PYTHON_CMD=""

# Check for python3.11 first
if check_python_version "python3.11"; then
    echo "Using python3.11"
elif check_python_version "python3.10"; then
    echo "Using python3.10"  
elif check_python_version "python3.9"; then
    echo "Using python3.9"
elif check_python_version "python3.8"; then
    echo "Using python3.8"
elif check_python_version "python3"; then
    echo "Using python3"
elif check_python_version "python"; then
    echo "Using python"
else
    echo "No compatible Python found (need 3.8+), installing Python 3.11..."
    
    # Install Homebrew if it's not installed
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found, installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH for this session
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f "/usr/local/bin/brew" ]]; then
            eval "$(/usr/local/bin/brew shellenv)"
        fi
    fi
    
    brew install python@3.11
    PYTHON_CMD="python3.11"
    
    if ! command -v "$PYTHON_CMD" &> /dev/null; then
        echo "Failed to install Python 3.11. Please install manually."
        exit 1
    fi
fi

# Create a virtual environment in the current directory
echo "Creating virtual environment..."
# Remove any existing venv to ensure clean install
rm -rf gui_venv
$PYTHON_CMD -m venv gui_venv

# Activate the virtual environment
echo "Activating virtual environment..."
source gui_venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# List files for debugging
echo "Files in the directory:"
ls -l

# Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Please make sure it is in the same directory."
fi

# Give a message to users about how to activate the venv manually if needed
echo "Installation completed successfully!"
echo ""
echo "=== Next Steps ==="
echo "• You can now run the application using start_ui.command"
echo "• Double-click start_ui.command to launch the UMTK UI"
echo "• If you encounter security warnings, see README_macOS.md for solutions"
echo ""
echo "=== Troubleshooting ==="
echo "• If blocked by Gatekeeper: Right-click → Open, then click 'Open' in dialog"
echo "• For permission errors: Run 'chmod +x *.command' in Terminal"
echo "• For other issues: Check README_macOS.md for detailed instructions"
echo ""

# Keep the terminal open for user interaction
exec "$SHELL"