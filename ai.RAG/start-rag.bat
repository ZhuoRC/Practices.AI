@echo off
echo ========================================
echo Starting RAG Intelligent Q&A System
echo ========================================
echo.

:: Check if backend virtual environment exists
if not exist "backend\venv\Scripts\activate.bat" (
    echo Error: Backend virtual environment not found!
    echo Please set up the backend first by running:
    echo   cd backend
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

:: Check if frontend node_modules exists
if not exist "frontend\node_modules" (
    echo Error: Frontend dependencies not found!
    echo Please install frontend dependencies first by running:
    echo   cd frontend
    echo   npm install
    pause
    exit /b 1
)

:: Start backend
echo Starting backend server...
start "RAG Backend" cmd /k "cd backend && venv\Scripts\activate && python run.py"

:: Wait a bit for backend to start
timeout /t 3 /nobreak > nul

:: Start frontend
echo Starting frontend server...
start "RAG Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Both servers are starting...
echo Backend: http://localhost:8001
echo Frontend: http://localhost:5173
echo ========================================
echo.
echo Press any key to stop both servers...
pause > nul

:: Stop servers (close the terminal windows)
taskkill /FI "WindowTitle eq RAG Backend*" /T /F > nul 2>&1
taskkill /FI "WindowTitle eq RAG Frontend*" /T /F > nul 2>&1

echo.
echo Servers stopped.
pause
