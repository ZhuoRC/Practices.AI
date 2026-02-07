@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 房产信息爬虫 - 启动脚本
echo ========================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\" (
    echo [1/3] 创建Python虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo 错误: 无法创建虚拟环境
        echo 请确保已安装Python 3.8+
        pause
        exit /b 1
    )
    echo ✓ 虚拟环境创建成功
    echo.
) else (
    echo [1/3] ✓ 虚拟环境已存在
    echo.
)

REM Activate virtual environment
echo [2/3] 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo 错误: 无法激活虚拟环境
    pause
    exit /b 1
)
echo ✓ 虚拟环境已激活
echo.

REM Install dependencies
echo [3/3] 安装依赖包...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)
echo ✓ 依赖安装完成
echo.

echo ========================================
echo 开始运行爬虫...
echo ========================================
echo.

REM Run the main script
python main.py %*

echo.
echo ========================================
echo 按任意键退出...
pause >nul
