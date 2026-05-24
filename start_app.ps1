# Dual Access Login Test - Startup Script
# This script will automatically activate the virtual environment and start the Flask app

Write-Host "🚀 Starting Dual Access Login Test Application..." -ForegroundColor Green

# Set execution policy for this session only (no permanent changes)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force

# Navigate to project directory
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Check if virtual environment is activated
if ($env:VIRTUAL_ENV) {
    Write-Host "✅ Virtual environment activated successfully!" -ForegroundColor Green
    
    # Start Flask application
    Write-Host "🌐 Starting Flask application..." -ForegroundColor Yellow
    Write-Host "📍 Application will be available at: http://127.0.0.1:5000" -ForegroundColor Cyan
    Write-Host "⏹️  Press Ctrl+C to stop the application" -ForegroundColor Red
    Write-Host ""
    
    # Run the Flask app
    python app.py
} else {
    Write-Host "❌ Failed to activate virtual environment!" -ForegroundColor Red
    Write-Host "Please check if the virtual environment exists in the 'venv' folder." -ForegroundColor Yellow
    pause
}
