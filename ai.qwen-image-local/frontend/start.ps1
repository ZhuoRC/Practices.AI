# PowerShell startup script for frontend
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Qwen Image Editor - Frontend Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if dependencies are installed
if (-not (Test-Path "node_modules")) {
    Write-Host "[1/2] First run, installing dependencies..." -ForegroundColor Yellow
    Write-Host ""
    npm install
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "Dependency installation failed!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host ""
    Write-Host "Dependencies installed successfully!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[1/2] Dependencies already installed, skipping" -ForegroundColor Green
    Write-Host ""
}

Write-Host "[2/2] Starting development server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Access URL: http://localhost:3500" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: Make sure backend API service is running (port 8500)" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start the server (PORT is set in .env file)
npm start
