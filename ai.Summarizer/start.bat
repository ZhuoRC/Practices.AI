@echo off
echo ============================================
echo   AI Summarizer - Starting Services
echo ============================================
echo.

:: Check if .env exists
if not exist "backend\.env" (
    echo [ERROR] backend\.env file not found!
    echo Please copy backend\.env.example to backend\.env and configure it.
    pause
    exit /b 1
)

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/4] Checking Python dependencies...
cd backend
if not exist "venv\" (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo [2/4] Installing/Updating Python dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

echo [3/4] Checking Node.js dependencies...
cd ..\frontend
if not exist "node_modules\" (
    echo Installing Node.js dependencies...
    call npm install
)

echo [4/4] Starting services...
echo.
echo ============================================
echo   Backend: http://localhost:8002
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8002/docs
echo ============================================
echo.
echo Press Ctrl+C to stop all services
echo.

:: Start backend in new window
cd ..\backend
start "AI Summarizer - Backend" cmd /k "venv\Scripts\activate.bat && python -m app.main"

:: Start frontend in new window
cd ..\frontend
start "AI Summarizer - Frontend" cmd /k "npm run dev"

echo Services started in separate windows!
echo Close this window or press any key to exit...

