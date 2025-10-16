@echo off
REM Change directory to where the script is located (so it works from anywhere)
cd /d "%~dp0"

REM Try to activate the virtual environment if it exists
if exist venv\Scripts\activate (
    echo Activating virtual environment...
    call venv\Scripts\activate
) else (
    echo No virtual environment found. Detecting system Python...
    
    REM Try different Python commands to find a suitable version
    set "PYTHON_CMD="
    
    python3.11 --version >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_CMD=python3.11"
        goto :run_app
    )
    
    python3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        for /f "tokens=2" %%v in ('python3 --version 2^>^&1') do (
            echo %%v | findstr /R "3\.[89]" >nul
            if %errorlevel% equ 0 (
                set "PYTHON_CMD=python3"
                goto :run_app
            )
            echo %%v | findstr /R "3\.1[0-9]" >nul
            if %errorlevel% equ 0 (
                set "PYTHON_CMD=python3"
                goto :run_app
            )
        )
    )
    
    python --version >nul 2>&1
    if %errorlevel% equ 0 (
        for /f "tokens=2" %%v in ('python --version 2^>^&1') do (
            echo %%v | findstr /R "3\.[89]" >nul
            if %errorlevel% equ 0 (
                set "PYTHON_CMD=python"
                goto :run_app
            )
            echo %%v | findstr /R "3\.1[0-9]" >nul
            if %errorlevel% equ 0 (
                set "PYTHON_CMD=python"
                goto :run_app
            )
        )
    )
    
    echo No compatible Python found. Please run install.bat first.
    pause
    exit /b 1
)

:run_app
REM Run the main.py file to start the UI
echo Starting the UI...
if defined PYTHON_CMD (
    %PYTHON_CMD% main.py
) else (
    python main.py
)
pause
