@echo off
chcp 65001 >nul
echo ========================================
echo    Qwen Image Editor - Detailed Diagnosis
echo ========================================
echo.

cd /d "%~dp0"

echo [1/6] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    goto :error
) else (
    echo OK: Python is installed
)
echo.

echo [2/6] Checking virtual environment...
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found
    echo Please run: install-deps.bat
    goto :error
) else (
    echo OK: Virtual environment exists
)
echo.

echo [3/6] Activating virtual environment and checking dependencies...
call .venv\Scripts\activate.bat

echo.
echo Checking Python dependencies in virtual environment...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: fastapi is not installed in venv
    goto :error
) else (
    echo OK: fastapi is installed
)

pip show uvicorn >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: uvicorn is not installed in venv
    goto :error
) else (
    echo OK: uvicorn is installed
)

pip show diffusers >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: diffusers is not installed in venv
    goto :error
) else (
    echo OK: diffusers is installed
)

pip show torch >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: torch is not installed in venv
    goto :error
) else (
    echo OK: torch is installed
)
echo.

echo [4/6] Checking if backend API can be imported...
python -c "from qwen_image_edit.qwen_image_edit_api import app; print('Backend API can be imported successfully')" 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Cannot import backend API
    echo This might be due to missing dependencies or model files
    goto :error
) else (
    echo OK: Backend API can be imported
)
echo.

echo [5/6] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    goto :error
) else (
    echo OK: Node.js is installed
)
echo.

echo [6/6] Checking frontend dependencies...
if not exist "frontend\node_modules" (
    echo ERROR: Frontend dependencies are not installed
    echo Run: cd frontend ^&^& npm install
    goto :error
) else (
    echo OK: Frontend dependencies are installed
)
echo.

echo [7/6] Checking if ports are in use...
netstat -ano | findstr :8500 >nul 2>&1
if %errorlevel% equ 0 (
    echo WARNING: Port 8500 is already in use
    echo Process using port 8500:
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8500') do @echo PID: %%a
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8500') do @tasklist /FI "PID eq %%a" /FO TABLE
) else (
    echo OK: Port 8500 is available
)
echo.

netstat -ano | findstr :3500 >nul 2>&1
if %errorlevel% equ 0 (
    echo WARNING: Port 3500 is already in use
    echo Process using port 3500:
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3500') do @echo PID: %%a
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3500') do @tasklist /FI "PID eq %%a" /FO TABLE
) else (
    echo OK: Port 3500 is available
)
echo.

echo ========================================
echo All checks passed successfully!
echo ========================================
echo.
echo You can now run: start.bat
echo.
goto :end

:error
echo.
echo ========================================
echo Diagnosis failed!
echo ========================================
echo.
echo Please fix the errors above before running start.bat
echo.

:end
pause