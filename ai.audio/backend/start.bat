@echo off
echo 🚀 AI Audio TTS Backend Startup
echo ================================

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Please create a virtual environment first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✅ Activating virtual environment...
call venv\Scripts\activate.bat

echo ✅ Installing dependencies (if needed)...
pip install -r requirements.txt

echo ✅ Starting backend on port 7000...
echo 📍 Backend will be available at: http://localhost:7000
echo 📍 API Documentation: http://localhost:7000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

pause