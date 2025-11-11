@echo off
echo Starting AI Audio TTS Application...
echo.

REM Check if directories exist
if not exist "backend" (
    echo Creating backend directory...
    mkdir backend
)

if not exist "frontend" (
    echo Creating frontend directory...
    mkdir frontend
)

REM Start backend in new window
echo Starting backend server...
start "Backend" cmd /c "start_backend.bat"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
echo Starting frontend server...
start "Frontend" cmd /c "start_frontend.bat"

echo Both servers should be starting...
echo Backend: http://localhost:7000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window
pause >nul
