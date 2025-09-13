@echo off
chcp 65001 >nul
title 关闭KSX后端服务

echo.
echo ========================================
echo    关闭KSX后端服务
echo ========================================
echo.

echo 🔍 检查运行中的后端服务...

REM 查找运行app.py的Python进程
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| findstr /C:"python.exe"') do (
    set "pid=%%i"
    set "pid=!pid:"=!"
    
    REM 检查这个进程是否在运行app.py
    wmic process where "ProcessId=!pid!" get CommandLine /format:list | findstr "app.py" >nul
    if !errorlevel! equ 0 (
        echo ✅ 找到后端服务进程: PID !pid!
        echo.
        echo 是否要关闭这个进程? (Y/N)
        set /p choice=
        if /i "!choice!"=="Y" (
            echo 🛑 正在关闭进程 !pid!...
            taskkill /PID !pid! /F
            if !errorlevel! equ 0 (
                echo ✅ 后端服务已关闭
            ) else (
                echo ❌ 关闭失败
            )
        ) else (
            echo ℹ️ 取消关闭
        )
        goto :end
    )
)

echo ℹ️ 未找到运行中的后端服务

:end
echo.
echo 按任意键退出...
pause >nul

