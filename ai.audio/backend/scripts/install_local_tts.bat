@echo off
echo Installing Free Local TTS Service (Piper TTS)
echo ================================================

echo.
echo This will install a completely free offline TTS service.
echo Total download size: ~250MB
echo.

REM Create models directory
if not exist "models" mkdir models
cd models

echo.
echo Step 1: Downloading Piper TTS engine...
curl -L -o piper.zip https://github.com/rhasspy/piper/releases/latest/download/piper_windows_amd64.zip
if %errorlevel% neq 0 (
    echo Failed to download Piper TTS
    pause
    exit /b 1
)

echo Extracting...
powershell -Command "Expand-Archive -Path 'piper.zip' -DestinationPath '.' -Force"
del piper.zip

echo.
echo Step 2: Downloading English voice model...
curl -L -o voice.tar.gz https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.tar.gz
if %errorlevel% neq 0 (
    echo Failed to download voice model
    pause
    exit /b 1
)

echo Extracting voice model...
powershell -Command "Expand-Archive -Path 'voice.tar.gz' -DestinationPath '.' -Force"
del voice.tar.gz

REM Rename files to match expected naming
if exist "en_US-lessac-medium.onnx" ren "en_US-lessac-medium.onnx" "en-us-lessac-medium.onnx"
if exist "en_US-lessac-medium.onnx.json" ren "en_US-lessac-medium.onnx.json" "en-us-lessac-medium.onnx.json"

echo.
echo =====================================
echo Installation Complete!
echo =====================================
echo.
echo Files downloaded:
echo - piper.exe (TTS engine)
echo - en-us-lessac-medium.onnx (voice model)
echo.
echo Next steps:
echo 1. Restart the backend server
echo 2. Select "local" provider in the frontend
echo 3. Choose "en-us-lessac-medium" voice
echo.
echo This service is completely FREE and works offline!
echo.

pause