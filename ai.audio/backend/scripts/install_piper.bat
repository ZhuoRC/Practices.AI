@echo off
echo Installing Piper TTS (Free Local TTS Service)
echo =============================================

echo.
echo This script will install Piper TTS and download English voice models.
echo Piper TTS is completely free and works offline.
echo.

REM Create models directory
if not exist "models" mkdir models
cd models

echo.
echo 1. Downloading Piper TTS for Windows...
echo    (This is a ~200MB download)
echo.

REM Download Piper TTS using curl
curl -L -o piper_windows_amd64.zip https://github.com/rhasspy/piper/releases/latest/download/piper_windows_amd64.zip

if %errorlevel% neq 0 (
    echo Failed to download Piper TTS
    echo Please check your internet connection
    pause
    exit /b 1
)

echo.
echo 2. Extracting Piper TTS...
powershell -Command "Expand-Archive -Path 'piper_windows_amd64.zip' -DestinationPath '.' -Force"

if %errorlevel% neq 0 (
    echo Failed to extract Piper TTS
    pause
    exit /b 1
)

echo.
echo 3. Downloading English voice model (Lessac Medium)...
echo    (This is a ~50MB download)
echo.

REM Download voice model
curl -L -o en_us_lessac_medium.tar.gz https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.tar.gz

if %errorlevel% neq 0 (
    echo Failed to download voice model
    pause
    exit /b 1
)

echo.
echo 4. Extracting voice model...
powershell -Command "Expand-Archive -Path 'en_us_lessac_medium.tar.gz' -DestinationPath '.' -Force"

REM Rename files to match expected format
if exist "en_US-lessac-medium.onnx" (
    ren "en_US-lessac-medium.onnx" "en-us-lessac-medium.onnx"
)
if exist "en_US-lessac-medium.onnx.json" (
    ren "en_US-lessac-medium.onnx.json" "en-us-lessac-medium.onnx.json"
)

echo.
echo 5. Cleaning up...
del piper_windows_amd64.zip
del en_us_lessac_medium.tar.gz

echo.
echo ✅ Installation Complete!
echo.
echo Piper TTS has been installed successfully.
echo.
echo Available voices:
echo - en-us-lessac-medium (English US Male)
echo.
echo You can now use the "local" provider in the AI Audio application.
echo.

pause