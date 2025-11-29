@echo off
echo Starting Video Subtitle Remover Frontend...
echo.

REM 检查Node.js是否安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM 检查frontend目录是否存在
if not exist "frontend" (
    echo Error: frontend directory not found
    echo Please ensure you are in the correct project directory
    pause
    exit /b 1
)

REM 切换到frontend目录
cd frontend

REM 检查package.json是否存在
if not exist "package.json" (
    echo Error: package.json not found in frontend directory
    echo This might not be a valid Node.js project
    pause
    exit /b 1
)

REM 检查node_modules是否存在，如果不存在则安装依赖
if not exist "node_modules" (
    echo Installing frontend dependencies...
    echo This may take a few minutes on first run...
    echo.
    npm install
    if %errorlevel% neq 0 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
    echo Dependencies installed successfully!
    echo.
)

REM 启动前端开发服务器
echo Starting frontend development server...
echo Frontend will be available at: http://localhost:3000
echo Press Ctrl+C to stop the server
echo.
npm run dev

REM 返回根目录
cd ..

pause
