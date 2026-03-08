@echo off
chcp 65001 >nul
echo ========================================
echo    Installing Backend Dependencies in Virtual Environment
echo ========================================
echo.

cd /d "%~dp0"

echo [1/6] Creating virtual environment...
if not exist ".venv" (
    echo Creating .venv...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo OK: Virtual environment created
) else (
    echo OK: Virtual environment already exists
)
echo.

echo [2/6] Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo OK: Virtual environment activated
echo.

echo [3/6] Upgrading pip...
python -m pip install --upgrade pip
echo.

echo [4/6] Installing PyTorch with CUDA support...
echo NOTE: If you don't have NVIDIA GPU, this will use CPU (slower)
echo.
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
echo.

echo [5/6] Installing diffusers from GitHub...
echo NOTE: PyPI version doesn't include QwenImageEditPipeline
echo.
pip install git+https://github.com/huggingface/diffusers
echo.

echo [6/6] Installing other dependencies from requirements.txt...
echo.
pip install -r requirements.txt
echo.

echo [7/6] Checking installation...
python -c "import diffusers; print('OK: diffusers installed')" 2>nul
if %errorlevel% neq 0 (
    echo ERROR: diffusers installation failed
) else (
    python -c "import fastapi; print('OK: fastapi installed')" 2>nul
    python -c "import uvicorn; print('OK: uvicorn installed')" 2>nul
)

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo IMPORTANT: The virtual environment (.venv) must be activated
echo before starting the application. The start scripts will
echo automatically activate it for you.
echo.
echo To manually activate the virtual environment:
echo   .venv\Scripts\activate.bat
echo.

pause
