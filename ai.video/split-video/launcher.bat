@echo off
echo ============================================
echo   AI Video Splitter - Quick Launcher
echo ============================================
echo.

cd /d "%~dp0"

:: Check if .env exists, if not copy from template
if not exist "backend\.env" (
    if exist "backend\.env.template" (
        echo Creating .env from template...
        copy "backend\.env.template" "backend\.env" >nul
    ) else (
        echo [ERROR] No .env or .env.template found!
        pause
        exit /b 1
    )
)

:: Start backend
cd backend
if exist "venv\Scripts\activate.bat" (
    start "Video Splitter - Backend [8801]" cmd /k "venv\Scripts\activate.bat && python run.py"
) else (
    echo [WARNING] Virtual environment not found. Run start.bat first to set up.
    start "Video Splitter - Backend [8801]" cmd /k "python run.py"
)

:: Wait a bit
timeout /t 2 /nobreak >nul

:: Start frontend
cd ..\frontend
if exist "node_modules\" (
    start "Video Splitter - Frontend [3801]" cmd /k "npm run dev"
) else (
    echo [WARNING] node_modules not found. Run start.bat first to set up.
    start "Video Splitter - Frontend [3801]" cmd /k "npm run dev"
)

echo.
echo Services launched!
echo Backend: http://localhost:8801
echo Frontend: http://localhost:3801
echo.
