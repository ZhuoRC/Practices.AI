@echo off
chcp 65001 >nul
echo ========================================
echo    Qwen Image Studio - Full Startup
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Starting image editing API service (Port 8500)...
echo.
start cmd /k "call .venv\Scripts\activate.bat && python qwen_image_edit/qwen_image_edit_api.py"

timeout /t 5 /nobreak >nul

echo [2/3] Starting text-to-image API service (Port 8501)...
echo.
start cmd /k "call .venv\Scripts\activate.bat && python qwen_image/qwen_image_api.py"

timeout /t 5 /nobreak >nul

echo [3/3] Starting frontend interface (Port 3500)...
echo.
start cmd /k "cd frontend && call start.bat"

echo.
echo ========================================
echo Services started successfully!
echo ========================================
echo.
echo Backend API (Image Edit): http://localhost:8500
echo Backend API (Image Gen):  http://localhost:8501
echo Frontend:                 http://localhost:3500
echo.
echo API Docs (Image Edit):    http://localhost:8500/docs
echo API Docs (Image Gen):     http://localhost:8501/docs
echo.
echo Note: Services are running in separate windows
echo Close the windows to stop the services
echo ========================================
echo.

pause