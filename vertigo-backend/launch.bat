@echo off
setlocal EnableDelayedExpansion

REM === Step 1: Define paths ===
set VENV_DIR=%cd%\env
set PYTHON_EXEC=%VENV_DIR%\Scripts\python.exe

REM === Step 2: Create virtual environment if not exists ===
if not exist "%PYTHON_EXEC%" (
    echo [INFO] Creating virtual environment...
    python -m venv "%VENV_DIR%"
)

REM === Step 3: Install requirements ===
echo [INFO] Installing dependencies...
"%PYTHON_EXEC%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    exit /b 1
)

REM === Step 4: Run the app ===
echo [INFO] Launching app...
start "" http://localhost:6166
call .\.venv\Scripts\activate.bat && python -m vertigo.py
if errorlevel 1 (
    echo [ERROR] Failed to launch app.
    exit /b 1
)

endlocal
