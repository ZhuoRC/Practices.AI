@echo off
title SadTalker Launcher
echo ========================================
echo    SadTalker Video Generator
echo ========================================
echo.
echo Starting services...
echo   Backend API: http://localhost:8802
echo   Frontend:    http://localhost:3802
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "web\node_modules" (
    echo [INFO] Installing frontend dependencies...
    cd web
    call npm install
    cd ..
)

REM Start backend in a new window
echo Starting backend server...
start "SadTalker Backend" cmd /k "call venv\Scripts\activate.bat && cd backend && python api.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in a new window
echo Starting frontend dev server...
start "SadTalker Frontend" cmd /k "cd web && npm run dev"

echo.
echo ========================================
echo Services starting...
echo.
echo   Backend API: http://localhost:8802
echo   Frontend:    http://localhost:3802
echo.
echo Press any key to open frontend in browser...
pause >nul

start http://localhost:3802
