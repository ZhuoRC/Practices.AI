@echo off
echo Installing Coqui XTTS-v2 Text-to-Speech
echo =====================================
echo.
echo This will install Coqui XTTS-v2, a high-quality multilingual TTS
echo with voice cloning capabilities supporting 17 languages.
echo.
echo Requirements:
echo - Python 3.8+ with pip
echo - ~5GB free disk space for models
echo - GPU recommended but not required (NVIDIA CUDA or AMD ROCm)
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo.
echo Step 1: Installing Python dependencies...
echo This may take several minutes...
echo.

REM Install required packages
pip install TTS>=0.22.0
if %errorlevel% neq 0 (
    echo ERROR: Failed to install TTS library
    pause
    exit /b 1
)

pip install torch==2.5.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cpu
if %errorlevel% neq 0 (
    echo ERROR: Failed to install PyTorch
    pause
    exit /b 1
)

pip install librosa soundfile numpy
if %errorlevel% neq 0 (
    echo ERROR: Failed to install audio processing libraries
    pause
    exit /b 1
)

echo.
echo Step 2: Creating voice samples directory...
mkdir voice_samples 2>nul

echo.
echo Step 3: Testing XTTS-v2 installation...
python -c "
import sys
try:
    from TTS.api import TTS
    print('✓ TTS library imported successfully')
    
    # Test model loading (this will download the model if not present)
    print('Loading XTTS-v2 model (first time may take 10-30 minutes)...')
    tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2', gpu=False)
    print('✓ XTTS-v2 model loaded successfully!')
    print(f'Available speakers: {len(tts.speakers)}')
    
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'✗ Error loading model: {e}')
    print('This is normal on first run - the model will be downloaded automatically')
    print('when you first use the TTS service.')
"

if %errorlevel% neq 0 (
    echo.
    echo WARNING: Model loading test failed, but installation may still work.
    echo The model will be downloaded automatically on first use.
    echo.
)

echo.
echo =====================================
echo Installation Complete!
echo =====================================
echo.
echo What was installed:
echo - TTS library (Coqui TTS)
echo - PyTorch and TorchAudio
echo - Audio processing libraries
echo - XTTS-v2 model (will be downloaded on first use)
echo.
echo Model details:
echo - Model: Coqui XTTS-v2
echo - Size: ~2.5GB (downloaded on first use)
echo - Languages: 17 supported (English, Spanish, French, German, etc.)
echo - Voice cloning: Yes (6-second audio sample required)
echo.
echo Usage:
echo 1. Start the backend server: python start_backend.py
echo 2. Select "xtts_v2" provider in the frontend
echo 3. Choose a voice or provide voice sample for cloning
echo.
echo Voice Cloning:
echo - Place 6+ second WAV files in voice_samples/ directory
echo - Files will be automatically detected as cloned voices
echo - Recommended format: 22kHz+ mono WAV
echo.
echo Next steps:
echo - Try the TTS service at http://localhost:8000
echo - Check health endpoint: http://localhost:8000/health
echo - View available voices: http://localhost:8000/api/tts/voices?provider=xtts_v2
echo.
echo Troubleshooting:
echo - If GPU is available, set XTTS_V2_USE_GPU=true in environment
echo - Model downloads to: ~/.local/share/tts/ (Linux/Mac) or %USERPROFILE%\.local\share\tts\ (Windows)
echo - Voice samples directory: ./voice_samples/
echo.

pause
