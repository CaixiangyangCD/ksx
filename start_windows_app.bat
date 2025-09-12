@echo off
chcp 65001 >nul
title KSX门店管理系统 - 启动器

echo.
echo ========================================
echo    KSX门店管理系统 - Windows启动器
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

REM 检查是否在项目根目录
if not exist "desktop\ksx_desktop_app.py" (
    echo ❌ 请在项目根目录运行此脚本
    echo 当前目录: %CD%
    pause
    exit /b 1
)

REM 检查前端构建文件
if not exist "frontend\dist\index.html" (
    echo ⚠️ 未找到前端构建文件，正在构建...
    echo.
    cd frontend
    if exist "package.json" (
        if exist "pnpm-lock.yaml" (
            echo 使用pnpm构建...
            pnpm run build
        ) else (
            echo 使用npm构建...
            npm run build
        )
    ) else (
        echo ❌ 未找到package.json文件
        pause
        exit /b 1
    )
    cd ..
    
    if not exist "frontend\dist\index.html" (
        echo ❌ 前端构建失败
        pause
        exit /b 1
    )
    echo ✅ 前端构建完成
)

REM 检查依赖
echo 🔍 检查依赖包...
python -c "import PySide6" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ PySide6未安装，正在安装...
    pip install PySide6 PySide6-Addons
)

python -c "from PySide6.QtWebEngineWidgets import QWebEngineView" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ QtWebEngine未安装，正在安装...
    pip install PySide6-WebEngine
)

REM 启动应用
echo.
echo 🚀 启动KSX门店管理系统...
echo 💡 首次运行时会自动安装Playwright浏览器，请耐心等待
echo.

python desktop\ksx_desktop_app.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 应用启动失败
    echo 请检查错误信息或联系技术支持
    pause
)

echo.
echo 应用已退出
pause
