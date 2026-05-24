@echo off
title Dual Access Login Test - Flask Application
color 0A

echo.
echo ========================================
echo   Dual Access Login Test Application
echo ========================================
echo.

REM Navigate to the script directory
cd /d "%~dp0"

echo [1/4] Setting up PowerShell execution policy...
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force" 2>nul

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Checking dependencies...
python -c "import flask_login" 2>nul
if errorlevel 1 (
    echo Installing missing dependencies...
    pip install -r requirements.txt
)

echo [4/4] Starting Flask application...
echo.
echo ========================================
echo   Application URL: http://127.0.0.1:5000
echo   Press Ctrl+C to stop the application
echo ========================================
echo.

python app.py

echo.
echo Application stopped. Press any key to exit...
pause >nul
