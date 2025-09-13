@echo off
chcp 65001 >nul
title KSX门店管理系统 - 后端开发服务器

echo.
echo ========================================
echo    KSX门店管理系统 - 后端开发服务器
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

python --version
echo ✅ Python环境正常

REM 检查是否在项目根目录
if not exist "backend\app.py" (
    echo ❌ 请在项目根目录运行此脚本
    echo 当前目录: %CD%
    pause
    exit /b 1
)

REM 检查依赖
echo 🔍 检查依赖包...
python -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ FastAPI未安装，正在安装...
    pip install fastapi uvicorn loguru
)

python -c "import playwright" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Playwright未安装，正在安装...
    pip install playwright requests beautifulsoup4 lxml
)

REM 启动后端服务器
echo.
echo 🚀 启动后端开发服务器...
echo 💡 后端服务将在 http://127.0.0.1:18888 运行
echo 💡 按 Ctrl+C 停止服务器
echo.

cd backend
python app.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 后端服务器启动失败
    echo 请检查错误信息或联系技术支持
    pause
)

echo.
echo 后端服务器已停止
pause
