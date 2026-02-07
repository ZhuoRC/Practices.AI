@echo off
title SadTalker Frontend
echo ========================================
echo    SadTalker Frontend Dev Server
echo ========================================
echo.

REM Check if node_modules exists
if not exist "web\node_modules" (
    echo [INFO] Installing dependencies...
    cd web
    call npm install
    cd ..
)

echo Starting frontend dev server on http://localhost:3802
echo Press Ctrl+C to stop
echo.

cd web
npm run dev
