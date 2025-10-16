@echo off
setlocal EnableDelayedExpansion

set VENV_DIR=%cd%\env
set PYTHON_EXEC=%VENV_DIR%\Scripts\python.exe

if not exist "%PYTHON_EXEC%" (
    echo [INFO] Creating virtual environment...
    python -m venv "%VENV_DIR%"
)

echo [INFO] Installing dependencies...
"%PYTHON_EXEC%" -m pip install -r requirements.txt || goto :error

REM === Run directly using venv python ===
echo [INFO] Launching app...
start /b "" "%PYTHON_EXEC%" vertigo.py
if errorlevel 1 (
    echo [ERROR] Failed to launch app.
    exit /b 1
)
start "" http://localhost:6166

