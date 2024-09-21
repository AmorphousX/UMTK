#!/bin/bash

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Run main.py script
if [ -f "main.py" ]; then
    echo "Running main.py..."
    python main.py
else
    echo "main.py not found. Please make sure it is in the same directory."
fi

# Keep the terminal open for user interaction
exec "$SHELL"
