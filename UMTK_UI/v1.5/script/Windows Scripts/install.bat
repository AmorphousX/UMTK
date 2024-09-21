@echo off
REM Change directory to the location of this script
cd /d "%~dp0"

REM Check if Python 3.11 is installed
python --version | findstr "3.11"
if %errorlevel% neq 0 (
    echo Python 3.11 is not installed.
    echo Downloading Python 3.11 installer...

    REM Download Python 3.11 installer
    curl -o python-3.11.exe https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe

    REM Install Python 3.11 silently and log installation
    echo Installing Python 3.11...
    start /wait python-3.11.exe /quiet InstallAllUsers=1 PrependPath=1

    REM Wait for 10 seconds to ensure installation completes
    timeout /t 10 /nobreak > nul

    REM Check if Python 3.11 was installed successfully
    python --version | findstr "3.11"
    if %errorlevel% neq 0 (
        echo Python installation failed or was not completed. Please install manually.
        del python-3.11.exe
        exit /b 1
    )
    REM Remove the installer after installation
    del python-3.11.exe
) else (
    echo Python 3.11 is already installed.
)

REM Create a virtual environment if it doesn't already exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

REM Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Check for requirements.txt
if not exist requirements.txt (
    echo ERROR: requirements.txt not found.
    echo Please ensure the requirements.txt file is present in the directory.
    pause
    exit /b 1
) else (
    echo Installing dependencies from requirements.txt...
    python -m pip install -r requirements.txt
)

echo Installation complete.
pause