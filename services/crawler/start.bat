@echo off
echo ========================================
echo     KSX数据爬虫启动脚本
echo ========================================
echo.

cd /d "%~dp0"

echo 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

echo.
echo 安装/更新依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo 警告: 依赖安装可能存在问题，但继续执行...
)

echo.
echo 启动KSX数据爬虫...
python main.py

echo.
echo 脚本执行完成
pause
