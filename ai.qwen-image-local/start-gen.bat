@echo off
chcp 65001 >nul
echo ========================================
echo    Qwen Image Studio - Text to Image
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] Starting text-to-image API service (Port 8501)...
echo.
echo Note: Using Z-Image model (lighter and faster than Qwen-Image)
echo Will automatically use GPU (4GB+) if available
echo.
start cmd /k "call .venv\Scripts\activate.bat && python qwen_image/qwen_image_api.py"

timeout /t 5 /nobreak >nul

echo [2/2] Starting frontend interface (Port 3500)...
echo.
start cmd /k "cd frontend && call start.bat"

echo.
echo ========================================
echo Services started successfully!
echo ========================================
echo.
echo Backend API (Image Gen):  http://localhost:8501
echo Frontend:                 http://localhost:3500
echo.
echo API Docs (Image Gen):     http://localhost:8501/docs
echo.
echo Note: Services are running in separate windows
echo Close the windows to stop the services
echo ========================================
echo.

pause