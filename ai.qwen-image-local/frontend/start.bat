@echo off
chcp 65001 >nul
echo ========================================
echo    Qwen 图像编辑器 - 前端启动
echo ========================================
echo.

cd /d "%~dp0"

REM 检查是否已安装依赖
if not exist "node_modules" (
    echo [1/2] 首次运行，正在安装依赖...
    echo.
    call npm install
    if %errorlevel% neq 0 (
        echo.
        echo ❌ 依赖安装失败！
        pause
        exit /b 1
    )
    echo.
    echo ✅ 依赖安装完成！
    echo.
) else (
    echo [1/2] 依赖已安装，跳过安装步骤
    echo.
)

echo [2/2] 启动开发服务器...
echo.
echo 🌐 访问地址: http://localhost:3500
echo.
echo 提示：请确保后端 API 服务已启动 (端口 8500)
echo 按 Ctrl+C 可停止服务器
echo.
echo ========================================
echo.

npm start

pause
