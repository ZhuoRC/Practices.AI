@echo off
echo ============================================
echo   AI Video Face Swap - Starting Services
echo ============================================
echo.

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

echo [1/4] Checking Python virtual environment...
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
echo   Backend: http://localhost:8802
echo   Frontend: http://localhost:3802
echo   API Docs: http://localhost:8802/docs
echo ============================================
echo.
echo Press Ctrl+C to stop all services
echo.

:: Start backend in new window
cd ..\backend
start "AI Video Face Swap - Backend" cmd /k "venv\Scripts\activate.bat && python run.py"

:: Wait a bit for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend in new window
cd ..\frontend
start "AI Video Face Swap - Frontend" cmd /k "npm run dev"

echo.
echo [DONE] Services started in separate windows!
echo.
echo IMPORTANT: First run will download AI models automatically
echo This may take several minutes depending on your internet speed.
echo.
echo Close this window or press any key to exit...
pause >nul
