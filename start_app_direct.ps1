# Dual Access Login Test - Direct PowerShell Launcher
# This script can be run directly by right-clicking and "Run with PowerShell"

Write-Host "🚀 Dual Access Login Test - Starting Application..." -ForegroundColor Green

# Set execution policy for this session only
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force -ErrorAction SilentlyContinue

# Get the directory where this script is located
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "📁 Project Directory: $scriptDir" -ForegroundColor Yellow

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
try {
    & ".\venv\Scripts\Activate.ps1"
    if ($env:VIRTUAL_ENV) {
        Write-Host "✅ Virtual environment activated successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to activate virtual environment!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-Host "❌ Error activating virtual environment: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check dependencies
Write-Host "🔍 Checking Flask dependencies..." -ForegroundColor Yellow
try {
    python -c "import flask_login, flask, flask_sqlalchemy" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "📦 Installing missing dependencies..." -ForegroundColor Yellow
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to install dependencies!" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
    } else {
        Write-Host "✅ All dependencies are available!" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Error checking dependencies: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Start Flask application
Write-Host "🌐 Starting Flask application..." -ForegroundColor Yellow
Write-Host "📍 Application will be available at: http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host "⏹️  Press Ctrl+C to stop the application" -ForegroundColor Red
Write-Host ""

try {
    python app.py
} catch {
    Write-Host "❌ Error starting Flask application: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "👋 Application stopped." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}
