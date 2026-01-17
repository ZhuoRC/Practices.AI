@echo off
echo ============================================
echo   AI Video Splitter - Starting Services
echo ============================================
echo.

:: Check if .env exists
if not exist "backend\.env" (
    echo [ERROR] backend\.env file not found!
    echo Please copy backend\.env.example to backend\.env and configure it.
    echo.
    echo Required configuration:
    echo - ZHIPU_API_KEY: Your Zhipu AI API key
    echo - WHISPER_MODEL: Whisper model size (base recommended)
    echo.
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

:: Check if ffmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] ffmpeg is not installed or not in PATH
    echo ffmpeg is required for video processing!
    echo Please install ffmpeg and add it to PATH
    pause
    exit /b 1
)

echo [1/5] Checking Python virtual environment...
cd backend
if not exist "venv\" (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo [2/5] Installing/Updating Python dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

echo [3/5] Checking Node.js dependencies...
cd ..\frontend
if not exist "node_modules\" (
    echo Installing Node.js dependencies...
    call npm install
)

echo [4/5] Starting services...
echo.
echo ============================================
echo   Backend: http://localhost:8801
echo   Frontend: http://localhost:3801
echo   API Docs: http://localhost:8801/docs
echo ============================================
echo.
echo Press Ctrl+C to stop all services
echo.

:: Start backend in new window
cd ..\backend
start "AI Video Splitter - Backend" cmd /k "venv\Scripts\activate.bat && python run.py"

:: Wait a bit for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend in new window
cd ..\frontend
start "AI Video Splitter - Frontend" cmd /k "npm run dev"

echo.
echo [5/5] Services started in separate windows!
echo.
echo IMPORTANT: First run will download Whisper model (~1-10GB)
echo This may take several minutes depending on your internet speed.
echo.
echo Close this window or press any key to exit...
pause >nul
