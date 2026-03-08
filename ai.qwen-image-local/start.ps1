# PowerShell startup script for Qwen Image Studio
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Qwen Image Studio - Full Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run install-deps.bat first to create the virtual environment." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[1/3] Starting image editing API service (Port 8500)..." -ForegroundColor Yellow
Write-Host ""
$editBackend = Start-Process -FilePath "cmd" -ArgumentList "/k call .venv\Scripts\activate.bat && python qwen_image_edit/qwen_image_edit_api.py" -PassThru -WindowStyle Normal
Start-Sleep -Seconds 5

Write-Host "[2/3] Starting text-to-image API service (Port 8501)..." -ForegroundColor Yellow
Write-Host ""
$genBackend = Start-Process -FilePath "cmd" -ArgumentList "/k call .venv\Scripts\activate.bat && python qwen_image/qwen_image_api.py" -PassThru -WindowStyle Normal
Start-Sleep -Seconds 5

Write-Host "[3/3] Starting frontend interface (Port 3500)..." -ForegroundColor Yellow
Write-Host ""
$frontend = Start-Process -FilePath "cmd" -ArgumentList "/k cd frontend && call start.bat" -PassThru -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Services started successfully!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API (Image Edit): http://localhost:8500" -ForegroundColor Green
Write-Host "Backend API (Image Gen):  http://localhost:8501" -ForegroundColor Green
Write-Host "Frontend:                 http://localhost:3500" -ForegroundColor Green
Write-Host ""
Write-Host "API Docs (Image Edit):    http://localhost:8500/docs" -ForegroundColor Gray
Write-Host "API Docs (Image Gen):     http://localhost:8501/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "Note: Services are running in separate windows" -ForegroundColor Yellow
Write-Host "Close the windows to stop the services" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit (services will continue running)"