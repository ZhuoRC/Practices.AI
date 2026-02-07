@echo off
title SadTalker Backend
echo ========================================
echo    SadTalker Backend Server
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting backend server on http://localhost:8802
echo Press Ctrl+C to stop
echo.

cd backend
python api.py
