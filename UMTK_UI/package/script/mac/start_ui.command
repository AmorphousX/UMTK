#!/bin/bash

# Change to the directory where the script is located
cd "$(dirname "$0")"

echo "=== UMTK UI Launcher ==="
echo ""

# Handle potential Gatekeeper issues
if [ -f "umtk-ui" ]; then
    echo "Checking PyInstaller binary for quarantine..."
    if xattr -l umtk-ui 2>/dev/null | grep -q "com.apple.quarantine"; then
        echo "Removing quarantine from umtk-ui binary..."
        xattr -dr com.apple.quarantine umtk-ui 2>/dev/null || true
        chmod +x umtk-ui
    fi
fi

echo "Starting application..."
echo ""

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

# Try to activate the virtual environment first
if [ -d "gui_venv" ] && [ -f "gui_venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source gui_venv/bin/activate
    PYTHON_CMD="python"
else
    echo "No virtual environment found. Detecting system Python..."
    
    # Try to find a suitable Python version
    PYTHON_CMD=""
    
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
        echo "No compatible Python found. Please run install.command first."
        read -p "Press any key to continue..."
        exit 1
    fi
fi

# Run main.py script
if [ -f "main.py" ]; then
    echo "Running main.py..."
    $PYTHON_CMD main.py
else
    echo "main.py not found. Please make sure it is in the same directory."
fi

# Keep the terminal open for user interaction
read -p "Press any key to continue..."
