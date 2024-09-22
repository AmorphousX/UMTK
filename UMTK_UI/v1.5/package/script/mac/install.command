#!/bin/bash

# Ask for the administrator password upfront to run privileged commands
sudo -v

# Store the current directory
current_dir=$(pwd)

# Ensure the script is executable
chmod +x "$0"

# Install Python 3.11 using Homebrew on macOS
if ! command -v python3.11 &> /dev/null
then
    echo "Python 3.11 not found, installing..."
    # Install Homebrew if it's not installed
    if ! command -v brew &> /dev/null
    then
        echo "Homebrew not found, installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install python@3.11
else
    echo "Python 3.11 is already installed."
fi

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Create a virtual environment in the current directory
echo "Creating virtual environment..."
python3.11 -m venv venv

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

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
echo "Setup is complete. The virtual environment is activated."
echo "To activate it manually later, run: source venv/bin/activate"

# Keep the terminal open for user interaction
exec "$SHELL"