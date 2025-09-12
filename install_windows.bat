@echo off
chcp 65001 >nul
echo  安装KSX门店管理系统...

REM 检查是否存在应用文件
if not exist "KSX门店管理系统.exe" (
    echo ❌ 未找到应用文件，请先运行构建脚本
    pause
    exit /b 1
)

REM 创建安装目录
set "INSTALL_DIR=%USERPROFILE%\KSX门店管理系统"
if not exist "%INSTALL_DIR%" (
    echo  创建安装目录: %INSTALL_DIR%
    mkdir "%INSTALL_DIR%"
)

REM 复制应用文件
echo  正在安装应用...
copy "KSX门店管理系统.exe" "%INSTALL_DIR%\"
if exist "playwright-browsers" (
    echo  复制浏览器文件...
    xcopy "playwright-browsers" "%INSTALL_DIR%\playwright-browsers\" /E /I /Y
)

REM 创建桌面快捷方式
echo  创建桌面快捷方式...
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\KSX门店管理系统.lnk"

REM 使用PowerShell创建快捷方式
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\KSX门店管理系统.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'KSX门店管理系统'; $Shortcut.Save()"

echo  安装完成！
echo  您可以在桌面找到KSX门店管理系统的快捷方式
echo  首次运行时会自动安装Playwright浏览器，请耐心等待
echo.
echo 按任意键退出...
pause >nul
