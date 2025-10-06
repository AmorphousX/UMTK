#!/bin/bash

# Change to the directory where the script is located
cd "$(dirname "$0")"

echo "Checking for compatible Python installation..."

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
    echo "No compatible Python found (need 3.8+), attempting to install..."
    
    # Detect package manager and install Python
    if command -v apt &> /dev/null; then
        echo "Using apt to install Python..."
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv
        PYTHON_CMD="python3"
    elif command -v yum &> /dev/null; then
        echo "Using yum to install Python..."
        sudo yum install -y python3 python3-pip
        PYTHON_CMD="python3"
    elif command -v dnf &> /dev/null; then
        echo "Using dnf to install Python..."
        sudo dnf install -y python3 python3-pip
        PYTHON_CMD="python3"
    elif command -v pacman &> /dev/null; then
        echo "Using pacman to install Python..."
        sudo pacman -S python python-pip
        PYTHON_CMD="python3"
    else
        echo "Could not detect package manager. Please install Python 3.8+ manually."
        exit 1
    fi
    
    # Verify installation
    if ! check_python_version "$PYTHON_CMD"; then
        echo "Failed to install compatible Python. Please install manually."
        exit 1
    fi
fi

# Create a virtual environment in the current directory
echo "Creating virtual environment..."
$PYTHON_CMD -m venv gui_venv

# Activate the virtual environment
echo "Activating virtual environment..."
source gui_venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Looking for it in the parent directory..."
    if [ -f "../../../requirements.txt" ]; then
        echo "Installing dependencies from ../../../requirements.txt..."
        pip install -r ../../../requirements.txt
    else
        echo "requirements.txt not found. Please ensure it's in the correct location."
        exit 1
    fi
fi

echo "Installation completed successfully!"
echo "You can now run the application using start_ui.sh"