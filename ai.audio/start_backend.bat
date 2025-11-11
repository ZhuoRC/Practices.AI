@echo off
echo Starting AI Audio TTS Backend...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if we're in the backend directory
if not exist "backend\main.py" (
    echo Error: backend\main.py not found
    echo Please run this script from the ai.audio directory
    pause
    exit /b 1
)

REM Create backend directory if it doesn't exist
if not exist "backend" mkdir backend
cd backend

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo Warning: requirements.txt not found
)

REM Create output directory
if not exist "generated_audio" mkdir generated_audio

REM Check for .env file
if not exist ".env" (
    echo Warning: .env file not found
    echo Please create .env file with your API keys
    echo Copy .env.example to .env and fill in your credentials
    echo.
)

REM Start the FastAPI server
echo Starting FastAPI server on http://localhost:7000
echo Press Ctrl+C to stop the server
echo.
python main.py

pause
