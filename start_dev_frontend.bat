@echo off
chcp 65001 >nul
title KSX门店管理系统 - 前端开发服务器

echo.
echo ========================================
echo    KSX门店管理系统 - 前端开发服务器
echo ========================================
echo.

REM 检查Node.js环境
echo 🔍 检查Node.js环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Node.js，请先安装Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

node --version
echo ✅ Node.js环境正常

REM 检查是否在项目根目录
if not exist "frontend\package.json" (
    echo ❌ 请在项目根目录运行此脚本
    echo 当前目录: %CD%
    pause
    exit /b 1
)

REM 检查前端依赖
echo 🔍 检查前端依赖...
cd frontend

if not exist "node_modules" (
    echo ⚠️ 前端依赖未安装，正在安装...
    if exist "pnpm-lock.yaml" (
        echo 使用pnpm安装依赖...
        pnpm install
    ) else (
        echo 使用npm安装依赖...
        npm install
    )
    
    if %errorlevel% neq 0 (
        echo ❌ 前端依赖安装失败
        cd ..
        pause
        exit /b 1
    )
    echo ✅ 前端依赖安装完成
)

REM 启动前端开发服务器
echo.
echo 🚀 启动前端开发服务器...
echo 💡 前端服务将在 http://localhost:5173 运行
echo 💡 按 Ctrl+C 停止服务器
echo.

if exist "pnpm-lock.yaml" (
    pnpm run dev
) else (
    npm run dev
)

if %errorlevel% neq 0 (
    echo.
    echo ❌ 前端开发服务器启动失败
    echo 请检查错误信息或联系技术支持
    pause
)

cd ..
echo.
echo 前端开发服务器已停止
pause
