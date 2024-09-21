@echo off
REM Change directory to where the script is located (so it works from anywhere)
cd /d "%~dp0"

REM Activate the virtual environment if it exists
if exist venv\Scripts\activate (
    echo Activating virtual environment...
    call venv\Scripts\activate
) else (
    echo No virtual environment found. Running with system Python...
)

REM Run the main.py file to start the UI
echo Starting the UI...
python main.py
pause
