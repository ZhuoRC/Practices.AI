@echo off
echo ========================================
echo AI Rewriter - Clean Start
echo ========================================
echo.
echo This script will:
echo - Stop all existing services
echo - Clear any cached data
echo - Restart both backend and frontend
echo.
pause

:: Kill existing processes
echo.
echo [1/5] Stopping existing services...
echo Checking port 8000 (Backend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    echo   - Stopping backend process %%a...
    taskkill /f /pid %%a >nul 2>&1
)

echo Checking port 3000 (Frontend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do (
    echo   - Stopping frontend process %%a...
    taskkill /f /pid %%a >nul 2>&1
)

echo Waiting for ports to be freed...
timeout /t 3 /nobreak >nul
echo   Done!

:: Backend setup
echo.
echo [2/5] Setting up backend...
cd backend

if not exist "venv" (
    echo   - Creating Python virtual environment...
    python -m venv venv
) else (
    echo   - Virtual environment exists
)

echo   - Activating virtual environment...
call venv\Scripts\activate.bat

echo   - Installing/Updating dependencies...
pip install -q -r requirements.txt

echo   - Checking .env configuration...
if not exist ".env" (
    echo   WARNING: .env file not found!
    echo   Please copy .env.example to .env and configure it.
    echo   Press any key to continue anyway...
    pause >nul
) else (
    echo   - .env file found
)

:: Frontend setup
echo.
echo [3/5] Setting up frontend...
cd ..\frontend

if not exist "node_modules" (
    echo   - Installing frontend dependencies...
    call npm install
) else (
    echo   - Dependencies already installed
)

:: Start services
echo.
echo [4/5] Starting services...
echo   - Starting backend server...
start "AI Rewriter Backend" cmd /k "cd /d %~dp0\backend && call venv\Scripts\activate.bat && python main.py"

echo   - Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo   - Starting frontend development server...
start "AI Rewriter Frontend" cmd /k "cd /d %~dp0\frontend && npm start"

:: Final info
echo.
echo [5/5] Startup complete!
echo.
echo ========================================
echo Application Information
echo ========================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo Logs:     backend\app.log
echo ========================================
echo.
echo Both services are starting in separate windows.
echo Please wait 10-30 seconds for frontend to fully load.
echo.
echo Troubleshooting:
echo - Check backend\app.log for detailed logs
echo - Ensure .env file is properly configured
echo - Verify API key and network connection
echo.
echo You can close this window - services will continue running.
echo.
pause
