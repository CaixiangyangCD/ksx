@echo off
chcp 65001 >nul
title KSX门店管理系统 - 开发模式启动器

echo.
echo ========================================
echo    KSX门店管理系统 - 开发模式启动器
echo ========================================
echo.

REM 检查Python环境
echo 🔍 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查Node.js环境
echo 🔍 检查Node.js环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Node.js，请先安装Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ 环境检查完成

REM 检查是否在项目根目录
if not exist "backend\app.py" (
    echo ❌ 请在项目根目录运行此脚本
    echo 当前目录: %CD%
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo ❌ 请在项目根目录运行此脚本
    echo 当前目录: %CD%
    pause
    exit /b 1
)

echo.
echo 📋 开发模式选项：
echo    1. 启动后端开发服务器 (FastAPI + 热重载)
echo    2. 启动前端开发服务器 (Vite + 热重载)
echo    3. 启动桌面应用 (PySide6 + 内置服务器)
echo    4. 同时启动前后端开发服务器 (推荐)
echo    5. 退出
echo.

set /p choice="请选择 (1-5): "

if "%choice%"=="1" (
    echo.
    echo 🚀 启动后端开发服务器...
    call start_dev_backend.bat
) else if "%choice%"=="2" (
    echo.
    echo 🚀 启动前端开发服务器...
    call start_dev_frontend.bat
) else if "%choice%"=="3" (
    echo.
    echo 🚀 启动桌面应用...
    python desktop\ksx_desktop_app.py
) else if "%choice%"=="4" (
    echo.
    echo 🚀 同时启动前后端开发服务器...
    echo 💡 将打开两个新的命令行窗口
    echo.
    start "KSX后端开发服务器" cmd /k start_dev_backend.bat
    timeout /t 3 /nobreak >nul
    start "KSX前端开发服务器" cmd /k start_dev_frontend.bat
    echo.
    echo ✅ 前后端开发服务器已启动
    echo 💡 后端: http://127.0.0.1:18888
    echo 💡 前端: http://localhost:5173
    echo.
    echo 按任意键关闭此窗口...
    pause >nul
) else if "%choice%"=="5" (
    echo 退出...
    exit /b 0
) else (
    echo ❌ 无效选择，请重新运行脚本
    pause
    exit /b 1
)

echo.
echo 开发模式已退出
pause
