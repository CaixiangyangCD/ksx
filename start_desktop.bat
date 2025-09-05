@echo off
chcp 65001 >nul
echo ========================================
echo KSX门店管理系统 - 桌面版启动器
echo ========================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo 正在检查依赖包...
pip show PySide6 >nul 2>&1
if errorlevel 1 (
    echo 正在安装PySide6...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

echo 正在检查构建文件...
if not exist "dist\index.html" (
    echo 错误: 未找到构建文件，请先构建Vue项目
    echo 运行: npm run build
    pause
    exit /b 1
)

echo 正在启动桌面应用...
python ksx_desktop_app.py

pause
