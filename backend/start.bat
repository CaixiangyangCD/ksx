@echo off
echo ========================================
echo     KSX数据查询API服务启动脚本
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
echo 启动API服务...
echo 服务将在 http://127.0.0.1:8080 启动
echo API文档地址: http://127.0.0.1:8080/docs
echo.
python main.py

echo.
echo 服务已停止
pause
