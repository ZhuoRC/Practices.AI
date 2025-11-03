@echo off
echo === AI Rewriter Application Starter ===
echo.
echo This will start both backend and frontend services.
echo Existing processes on ports 8000 and 3000 will be stopped.
echo.

:: Kill existing processes
echo Stopping existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    echo Stopping backend process %%a...
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do (
    echo Stopping frontend process %%a...
    taskkill /f /pid %%a >nul 2>&1
)

echo Waiting for ports to be free...
timeout /t 3 /nobreak >nul

echo.
echo === Starting Backend ===
cd backend
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo Starting backend server...
start "AI Rewriter Backend" cmd /k "cd /d %~dp0\backend && venv\Scripts\activate.bat && python main.py"

echo.
echo === Starting Frontend ===
cd ..\frontend
if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install
)

echo Starting frontend development server...
start "AI Rewriter Frontend" cmd /k "cd /d %~dp0\frontend && npm start"

echo.
echo =================================================
echo AI Rewriter Application Started!
echo =================================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo =================================================
echo.
echo Both services are starting in separate windows.
echo You can close this window - the services will continue running.
echo.
pause