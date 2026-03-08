@echo off
chcp 65001 >nul
echo ========================================
echo    Qwen Image Editor - Test Startup
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] Starting backend API service...
echo.
start "Qwen Backend" cmd /k "cd /d %~dp0 && call .venv\Scripts\activate.bat && python qwen_image_edit/qwen_image_edit_api.py"

timeout /t 5 /nobreak >nul

echo [2/2] Starting frontend interface...
echo.
cd frontend
start "Qwen Frontend" cmd /k "cd /d %~dp0frontend && set PORT=3500 && npm start"

echo.
echo ========================================
echo Services started in separate windows
echo ========================================
echo.
echo Backend API: http://localhost:8500
echo Frontend: http://localhost:3500
echo API Docs: http://localhost:8500/docs
echo.
echo Check the windows for any error messages
echo ========================================
echo.

pause