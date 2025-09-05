@echo off
chcp 65001 >nul
echo ========================================
echo KSX门店管理系统 - Web版启动器
echo ========================================
echo.

echo 正在检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Node.js，请先安装Node.js 16+
    pause
    exit /b 1
)

echo 正在检查npm环境...
npm --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到npm，请先安装npm
    pause
    exit /b 1
)

echo 正在安装项目依赖...
if not exist "node_modules" (
    npm install
    if errorlevel 1 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

echo 正在启动Web应用...
echo.
echo 应用将在浏览器中自动打开
echo 如果没有自动打开，请手动访问: http://localhost:3000
echo.
echo 按 Ctrl+C 停止服务器
echo.

npm run dev

pause
