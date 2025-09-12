@echo off
chcp 65001 >nul
title KSX门店管理系统 - Windows开发环境设置

echo.
echo ========================================
echo    KSX门店管理系统 - 开发环境设置
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

REM 检查Node.js环境
echo.
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

REM 检查pnpm
echo.
echo 🔍 检查pnpm...
pnpm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ 未找到pnpm，正在安装...
    npm install -g pnpm
    if %errorlevel% neq 0 (
        echo ❌ pnpm安装失败
        pause
        exit /b 1
    )
)

pnpm --version
echo ✅ pnpm环境正常

REM 安装Python依赖
echo.
echo 📦 安装Python依赖...
if exist "requirements.txt" (
    echo 使用requirements.txt安装依赖...
    pip install -r requirements.txt
) else if exist "pyproject.toml" (
    echo 使用uv安装依赖...
    uv sync
) else (
    echo 手动安装核心依赖...
    pip install PySide6 PySide6-Addons PySide6-WebEngine
    pip install fastapi uvicorn loguru
    pip install playwright requests beautifulsoup4 lxml
    pip install openpyxl pandas pillow pyinstaller
)

if %errorlevel% neq 0 (
    echo ❌ Python依赖安装失败
    pause
    exit /b 1
)

echo ✅ Python依赖安装完成

REM 安装前端依赖
echo.
echo 📦 安装前端依赖...
cd frontend
if exist "package.json" (
    if exist "pnpm-lock.yaml" (
        echo 使用pnpm安装前端依赖...
        pnpm install
    ) else (
        echo 使用npm安装前端依赖...
        npm install
    )
    
    if %errorlevel% neq 0 (
        echo ❌ 前端依赖安装失败
        cd ..
        pause
        exit /b 1
    )
    
    echo ✅ 前端依赖安装完成
    
    REM 构建前端
    echo.
    echo 🏗️ 构建前端项目...
    if exist "pnpm-lock.yaml" (
        pnpm run build
    ) else (
        npm run build
    )
    
    if %errorlevel% neq 0 (
        echo ❌ 前端构建失败
        cd ..
        pause
        exit /b 1
    )
    
    echo ✅ 前端构建完成
) else (
    echo ❌ 未找到package.json文件
    cd ..
    pause
    exit /b 1
)

cd ..

REM 安装Playwright浏览器
echo.
echo 🌐 安装Playwright浏览器...
python -m playwright install chromium
if %errorlevel% neq 0 (
    echo ⚠️ Playwright浏览器安装失败，将在首次运行时自动安装
) else (
    echo ✅ Playwright浏览器安装完成
)

REM 创建启动脚本
echo.
echo 📝 创建启动脚本...
echo @echo off > start_dev.bat
echo chcp 65001 ^>nul >> start_dev.bat
echo title KSX门店管理系统 - 开发模式 >> start_dev.bat
echo echo 🚀 启动KSX门店管理系统 - 开发模式... >> start_dev.bat
echo python desktop\ksx_desktop_app.py >> start_dev.bat
echo pause >> start_dev.bat

echo ✅ 启动脚本创建完成

echo.
echo ========================================
echo           设置完成！
echo ========================================
echo.
echo 📋 使用说明：
echo    1. 运行 start_dev.bat 启动开发模式
echo    2. 运行 start_windows_app.bat 启动应用
echo    3. 运行 build_windows.py 构建Windows版本
echo.
echo 💡 提示：
echo    - 首次运行时会自动安装Playwright浏览器
echo    - 开发模式下会显示更多调试信息
echo    - 如有问题请检查Python和Node.js版本
echo.

pause
