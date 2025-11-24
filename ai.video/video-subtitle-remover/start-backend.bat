@echo off
echo Starting Video Subtitle Remover Backend API...
echo.

REM 检查videoEnv虚拟环境是否存在
if not exist "videoEnv\Scripts\activate.bat" (
    echo Error: videoEnv virtual environment not found
    echo Please create videoEnv first using:
    echo python -m venv videoEnv
    echo videoEnv\Scripts\activate
    echo pip install -r requirements.txt
    pause
    exit /b 1
)

REM 激活虚拟环境
echo Activating videoEnv virtual environment...
call videoEnv\Scripts\activate.bat

REM 检查是否安装了依赖
if not exist "requirements.txt" (
    echo Error: requirements.txt not found in project directory
    pause
    exit /b 1
)

REM 安装依赖（如果需要）
echo Installing Python dependencies...
pip install -r requirements.txt

REM 切换到backend目录
cd backend

REM 启动API服务
echo.
echo Starting API server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python api.py

REM 停用时停用虚拟环境
call deactivate

pause
