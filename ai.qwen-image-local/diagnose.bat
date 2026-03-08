@echo off
chcp 65001 >nul
echo ========================================
echo    Qwen Image Editor - Diagnosis
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
) else (
    echo OK: Python is installed
)
echo.

echo [2/4] Checking Python dependencies...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: fastapi is not installed
) else (
    echo OK: fastapi is installed
)

pip show uvicorn >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: uvicorn is not installed
) else (
    echo OK: uvicorn is installed
)
echo.

echo [3/4] Checking Node.js installation...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
) else (
    echo OK: Node.js is installed
)
echo.

echo [4/4] Checking frontend dependencies...
if not exist "frontend\node_modules" (
    echo ERROR: Frontend dependencies are not installed
    echo Run: cd frontend ^&^& npm install
) else (
    echo OK: Frontend dependencies are installed
)
echo.

echo [5/4] Checking if ports are in use...
netstat -ano | findstr :8500 >nul 2>&1
if %errorlevel% equ 0 (
    echo WARNING: Port 8500 is already in use
) else (
    echo OK: Port 8500 is available
)

netstat -ano | findstr :3500 >nul 2>&1
if %errorlevel% equ 0 (
    echo WARNING: Port 3500 is already in use
) else (
    echo OK: Port 3500 is available
)
echo.

echo ========================================
echo Diagnosis complete
echo ========================================
echo.

pause