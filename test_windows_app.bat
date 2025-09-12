@echo off
chcp 65001 >nul
title KSX门店管理系统 - 简单测试

echo.
echo ========================================
echo    KSX门店管理系统 - 简单测试
echo ========================================
echo.

REM 检查应用文件是否存在
if not exist "dist\KSX门店管理系统.exe" (
    echo ❌ 未找到应用文件: dist\KSX门店管理系统.exe
    pause
    exit /b 1
)

echo ✅ 找到应用文件: dist\KSX门店管理系统.exe
echo.

REM 设置环境变量
set PYTHONUNBUFFERED=1
set QT_DEBUG_PLUGINS=1

echo 🚀 启动应用...
echo 💡 请观察应用窗口和控制台输出
echo.

REM 直接运行应用，不重定向输出，这样可以看到所有信息
cd dist
"KSX门店管理系统.exe"

echo.
echo 应用已退出
pause
