# Dual Access Login Test - PowerShell Profile
# This will automatically set up your project every time you open PowerShell in this directory

function Start-DualAccessApp {
    Write-Host "🚀 Starting Dual Access Login Test Application..." -ForegroundColor Green
    
    # Set execution policy for this session
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force -ErrorAction SilentlyContinue
    
    # Navigate to project directory
    $projectDir = "C:\Users\DELL\OneDrive\Desktop\cloud\dual-access-login-test"
    Set-Location $projectDir
    
    # Activate virtual environment
    Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
    
    if ($env:VIRTUAL_ENV) {
        Write-Host "✅ Virtual environment activated!" -ForegroundColor Green
        
        # Check and install dependencies if needed
        Write-Host "🔍 Checking dependencies..." -ForegroundColor Yellow
        python -c "import flask_login" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "📦 Installing missing dependencies..." -ForegroundColor Yellow
            pip install -r requirements.txt
        }
        
        Write-Host "🌐 Starting Flask application..." -ForegroundColor Yellow
        Write-Host "📍 Application: http://127.0.0.1:5000" -ForegroundColor Cyan
        Write-Host "⏹️  Press Ctrl+C to stop" -ForegroundColor Red
        Write-Host ""
        
        python app.py
    } else {
        Write-Host "❌ Failed to activate virtual environment!" -ForegroundColor Red
    }
}

# Create alias for easy access
Set-Alias -Name "startapp" -Value "Start-DualAccessApp"
Set-Alias -Name "run" -Value "Start-DualAccessApp"

Write-Host "🎯 Dual Access Login Test - PowerShell Profile Loaded!" -ForegroundColor Green
Write-Host "💡 Type 'startapp' or 'run' to start your application instantly!" -ForegroundColor Cyan
Write-Host "💡 Or just type '.\start_app.bat' to use the batch file" -ForegroundColor Cyan
