@echo off
chcp 65001 >nul
title KSX门店管理系统 - 桌面应用

echo 🚀 KSX门店管理系统 - 桌面应用
echo ================================================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python
    echo 请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

REM 启动应用
python ksx_desktop_app.py

pause
