@echo off
echo ========================================
echo SadTalker Video Generator Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Create virtual environment
echo [1/5] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
)

REM Activate virtual environment
echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [3/5] Upgrading pip...
python -m pip install --upgrade pip

REM Install PyTorch with CUDA support
echo [4/5] Installing PyTorch with CUDA 11.8 support...
echo (Change this command if you have different CUDA version or want CPU only)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

REM Install other dependencies
echo [5/5] Installing other dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Setup completed!
echo ========================================
echo.
echo Next steps:
echo 1. Download SadTalker checkpoints:
echo    - Visit https://github.com/OpenTalker/SadTalker#2-download-models
echo    - Place checkpoints in SadTalker/checkpoints folder
echo.
echo 2. Run the server:
echo    run.bat
echo.
pause
