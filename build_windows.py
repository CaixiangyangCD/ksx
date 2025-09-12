#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows版本的KSX应用构建脚本
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def main():
    print(" 开始构建KSX应用 (Windows版本)")
    
    # 检查操作系统
    if platform.system() != "Windows":
        print("❌ 此脚本仅支持Windows系统")
        return False
    
    print(f" 操作系统: {platform.system()}")
    print(f" Python版本: {sys.version}")
    print(f" 当前目录: {os.getcwd()}")
    
    # 项目根目录
    project_root = Path(__file__).parent
    
    # 清理构建目录
    print(" 清理构建目录...")
    build_dir = project_root / "build"
    dist_dir = project_root / "dist"
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # 构建前端项目
    print(" 构建前端项目...")
    frontend_dir = project_root / "frontend"
    os.chdir(frontend_dir)
    
    # 检查pnpm是否安装
    build_cmd = None
    
    # 尝试pnpm
    try:
        result = subprocess.run("pnpm --version", shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f" 检测到pnpm版本: {result.stdout.strip()}")
            build_cmd = "pnpm run build"
        else:
            print(f"⚠️ pnpm命令返回错误: {result.stderr}")
    except FileNotFoundError:
        print("⚠️ pnpm未找到")
    except subprocess.TimeoutExpired:
        print("⚠️ pnpm命令超时")
    except Exception as e:
        print(f"⚠️ 检查pnpm时出错: {e}")
    
    # 如果pnpm不可用，尝试npm
    if build_cmd is None:
        print("⚠️ pnpm不可用，尝试使用npm...")
        try:
            result = subprocess.run("npm --version", shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f" 检测到npm版本: {result.stdout.strip()}")
                build_cmd = "npm run build"
            else:
                print(f"⚠️ npm命令返回错误: {result.stderr}")
        except FileNotFoundError:
            print("⚠️ npm未找到")
        except subprocess.TimeoutExpired:
            print("⚠️ npm命令超时")
        except Exception as e:
            print(f"⚠️ 检查npm时出错: {e}")
    
    # 如果都不可用，返回错误
    if build_cmd is None:
        print("❌ 未找到pnpm或npm，请先安装Node.js")
        return False
    
    result = subprocess.run(build_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 前端构建失败: {result.stderr}")
        return False
    
    print(" 前端构建完成")
    
    # 回到项目根目录
    os.chdir(project_root)
    
    # 使用PyInstaller和Windows spec文件构建
    print(" 使用PyInstaller构建Windows应用...")
    
    # 使用Windows专用的.spec文件构建
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "ksx_app_windows.spec"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 构建失败: {result.stderr}")
        return False
    
    print(" Windows应用构建完成")
    
    # 创建Windows安装脚本
    print(" 创建Windows安装脚本...")
    install_script = project_root / "install_windows.bat"
    with open(install_script, "w", encoding="utf-8") as f:
        f.write("""@echo off
chcp 65001 >nul
echo  安装KSX门店管理系统...

REM 检查是否存在应用文件
if not exist "KSX门店管理系统.exe" (
    echo ❌ 未找到应用文件，请先运行构建脚本
    pause
    exit /b 1
)

REM 创建安装目录
set "INSTALL_DIR=%USERPROFILE%\\KSX门店管理系统"
if not exist "%INSTALL_DIR%" (
    echo  创建安装目录: %INSTALL_DIR%
    mkdir "%INSTALL_DIR%"
)

REM 复制应用文件
echo  正在安装应用...
copy "KSX门店管理系统.exe" "%INSTALL_DIR%\\"
if exist "playwright-browsers" (
    echo  复制浏览器文件...
    xcopy "playwright-browsers" "%INSTALL_DIR%\\playwright-browsers\\" /E /I /Y
)

REM 创建桌面快捷方式
echo  创建桌面快捷方式...
set "DESKTOP=%USERPROFILE%\\Desktop"
set "SHORTCUT=%DESKTOP%\\KSX门店管理系统.lnk"

REM 使用PowerShell创建快捷方式
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\\KSX门店管理系统.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'KSX门店管理系统'; $Shortcut.Save()"

echo  安装完成！
echo  您可以在桌面找到KSX门店管理系统的快捷方式
echo  首次运行时会自动安装Playwright浏览器，请耐心等待
echo.
echo 按任意键退出...
pause >nul
""")
    
    print(" Windows安装脚本创建完成")
    print(f" 输出目录: {dist_dir}")
    print(f" 应用程序: {dist_dir}/KSX门店管理系统.exe")
    print(f" 安装脚本: {install_script}")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n Windows构建成功！")
            print(" 提示：首次运行时会自动安装Playwright浏览器")
            print(" 使用说明：")
            print("   1. 运行 install_windows.bat 安装应用")
            print("   2. 或直接运行 dist/KSX门店管理系统.exe")
        else:
            print("\n❌ Windows构建失败！")
            sys.exit(1)
    except Exception as e:
        print(f"\n 构建过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
