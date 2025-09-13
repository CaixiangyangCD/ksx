@echo off
setlocal enabledelayedexpansion
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

REM 检查端口是否被占用
echo 🔍 检查端口18888是否被占用...
netstat -ano | findstr :18888 >nul
if %errorlevel% equ 0 (
    echo ⚠️ 端口18888已被占用！
    echo.
    echo 当前占用端口的进程：
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :18888 ^| findstr LISTENING') do (
        set "pid=%%a"
        echo   进程ID: !pid!
        wmic process where "ProcessId=!pid!" get ProcessId,CommandLine /format:list | findstr "CommandLine" | findstr /v "CommandLine="
    )
    echo.
    echo 请选择操作：
    echo 1. 关闭占用端口的进程并继续启动
    echo 2. 退出脚本
    echo 3. 强制启动（可能失败）
    set /p choice="请输入选择 (1/2/3): "
    
    if "!choice!"=="1" (
        echo 🛑 正在关闭占用端口的进程...
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr :18888 ^| findstr LISTENING') do (
            taskkill /PID %%a /F >nul 2>&1
        )
        echo ✅ 进程已关闭，等待2秒...
        timeout /t 2 /nobreak >nul
    ) else if "!choice!"=="2" (
        echo ℹ️ 退出启动
        pause
        exit /b 0
    ) else if "!choice!"=="3" (
        echo ⚠️ 强制启动，可能会失败
    ) else (
        echo ❌ 无效选择，退出
        pause
        exit /b 1
    )
) else (
    echo ✅ 端口18888可用
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
    echo 可能的原因：
    echo   - 端口被占用
    echo   - 依赖包缺失
    echo   - 配置文件错误
    echo 请检查错误信息或联系技术支持
    pause
)

echo.
echo 后端服务器已停止
pause
