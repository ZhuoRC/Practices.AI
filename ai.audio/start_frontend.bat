@echo off
echo Starting AI Audio TTS Frontend...
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js 16 or higher from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: npm is not installed or not in PATH
    echo Please install npm (usually comes with Node.js)
    pause
    exit /b 1
)

echo Node.js and npm are available
echo.

REM Check if frontend directory exists
if not exist "frontend" (
    echo Error: frontend directory not found
    echo Please run this script from the ai.audio directory
    pause
    exit /b 1
)

REM Check if package.json exists
if not exist "frontend\package.json" (
    echo Error: frontend\package.json not found
    echo Please ensure the frontend project is properly set up
    pause
    exit /b 1
)

cd frontend

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    echo This may take a few minutes...
    npm install
    if %errorlevel% neq 0 (
        echo Failed to install dependencies
        echo Please check your internet connection and try again
        pause
        exit /b 1
    )
    echo Dependencies installed successfully
) else (
    echo Dependencies already installed
)

REM Check for .env file for frontend (use existing .envX if it exists)
if not exist ".env" (
    if exist ".envX" (
        echo Found .envX file, copying to .env...
        copy ".envX" ".env" >nul
    ) else (
        echo Creating frontend .env file...
        echo REACT_APP_API_URL=http://localhost:7000 > .env
        echo Created .env file with default API URL
        echo You can modify this if your backend runs on a different port
    )
)

echo.
echo Starting React development server...
echo The server will be available at: http://localhost:3000
echo Press Ctrl+C to stop the server
echo.
npm start

pause
