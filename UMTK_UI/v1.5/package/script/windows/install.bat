@echo off
REM Change directory to the location of this script
cd /d "%~dp0"

REM Function to check Python version and compatibility
echo Checking for compatible Python installation...

REM Try different Python commands to find a suitable version
set "PYTHON_CMD="
set "PYTHON_VERSION="

REM Check for python3.11 specifically
python3.11 --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python3.11"
    for /f "tokens=2" %%v in ('python3.11 --version 2^>^&1') do set "PYTHON_VERSION=%%v"
    goto :found_python
)

REM Check for python3
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%v in ('python3 --version 2^>^&1') do (
        echo %%v | findstr /R "3\.[89]" >nul
        if %errorlevel% equ 0 (
            set "PYTHON_CMD=python3"
            set "PYTHON_VERSION=%%v"
            goto :found_python
        )
        echo %%v | findstr /R "3\.1[0-9]" >nul
        if %errorlevel% equ 0 (
            set "PYTHON_CMD=python3"
            set "PYTHON_VERSION=%%v"
            goto :found_python
        )
    )
)

REM Check for python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do (
        echo %%v | findstr /R "3\.[89]" >nul
        if %errorlevel% equ 0 (
            set "PYTHON_CMD=python"
            set "PYTHON_VERSION=%%v"
            goto :found_python
        )
        echo %%v | findstr /R "3\.1[0-9]" >nul
        if %errorlevel% equ 0 (
            set "PYTHON_CMD=python"
            set "PYTHON_VERSION=%%v"
            goto :found_python
        )
    )
)

REM If no suitable Python found, install Python 3.11
echo No compatible Python version found (need 3.8+).
echo Downloading Python 3.11 installer...

REM Download Python 3.11 installer
curl -o python-3.11.exe https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe

REM Install Python 3.11 silently and log installation
echo Installing Python 3.11...
start /wait python-3.11.exe /quiet InstallAllUsers=1 PrependPath=1

REM Wait for 10 seconds to ensure installation completes
timeout /t 10 /nobreak > nul

REM Check if Python 3.11 was installed successfully
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python installation failed or was not completed. Please install manually.
    del python-3.11.exe
    exit /b 1
)
set "PYTHON_CMD=python"
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%v"
REM Remove the installer after installation
del python-3.11.exe

:found_python
echo Found compatible Python: %PYTHON_CMD% %PYTHON_VERSION%

REM Remove any existing venv to ensure clean install
if exist "venv" (
    echo Removing existing virtual environment...
    rmdir /s /q "venv"
)

REM Create a virtual environment if it doesn't already exist
echo Creating virtual environment...
%PYTHON_CMD% -m venv venv

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