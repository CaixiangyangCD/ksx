#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建Windows安装包
支持创建NSIS安装包和便携版压缩包
"""

import os
import sys
import subprocess
import shutil
import zipfile
import platform
from pathlib import Path
from datetime import datetime

def create_nsis_installer():
    """创建NSIS安装包"""
    print("🚀 开始创建NSIS安装包...")
    
    # 检查dist目录
    dist_dir = Path("dist")
    exe_path = dist_dir / "KSX门店管理系统.exe"
    
    if not exe_path.exists():
        print("❌ 找不到应用文件，请先运行 python build_windows.py")
        return False
    
    # 检查NSIS是否安装
    try:
        subprocess.run(["makensis", "/VERSION"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 未找到NSIS，请先安装NSIS")
        print("下载地址: https://nsis.sourceforge.io/Download")
        return False
    
    # 创建NSIS脚本
    nsis_script = create_nsis_script()
    
    # 创建安装包
    installer_name = f"KSX门店管理系统_Setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.exe"
    installer_path = dist_dir / installer_name
    
    print("📦 创建NSIS安装包...")
    try:
        cmd = ["makensis", str(nsis_script)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ NSIS安装包创建成功: {installer_path}")
            
            # 显示文件大小
            if installer_path.exists():
                size_mb = installer_path.stat().st_size / (1024 * 1024)
                print(f"📊 安装包大小: {size_mb:.1f} MB")
            
            return True
        else:
            print(f"❌ NSIS安装包创建失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 创建NSIS安装包时出错: {e}")
        return False

def create_nsis_script():
    """创建NSIS安装脚本"""
    script_content = '''!define APPNAME "KSX门店管理系统"
!define COMPANYNAME "KSX"
!define DESCRIPTION "KSX门店管理系统"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/your-repo/ksx"
!define UPDATEURL "https://github.com/your-repo/ksx"
!define ABOUTURL "https://github.com/your-repo/ksx"
!define INSTALLSIZE 500000

RequestExecutionLevel admin
InstallDir "$PROGRAMFILES\\${APPNAME}"
Name "${APPNAME}"
Icon "dist\\KSX门店管理系统.exe"
outFile "dist\\KSX门店管理系统_Setup.exe"

!include LogicLib.nsh

page directory
page instfiles

!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin"
    messageBox mb_iconstop "需要管理员权限来安装此软件。"
    setErrorLevel 740
    quit
${EndIf}
!macroend

function .onInit
    setShellVarContext all
    !insertmacro VerifyUserIsAdmin
functionEnd

section "install"
    setOutPath $INSTDIR
    file "dist\\KSX门店管理系统.exe"
    
    # 复制浏览器文件
    setOutPath "$INSTDIR\\playwright-browsers"
    file /r "dist\\playwright-browsers\\*"
    
    writeUninstaller "$INSTDIR\\uninstall.exe"
    
    createDirectory "$SMPROGRAMS\\${APPNAME}"
    createShortCut "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk" "$INSTDIR\\KSX门店管理系统.exe" "" "$INSTDIR\\KSX门店管理系统.exe"
    createShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\KSX门店管理系统.exe" "" "$INSTDIR\\KSX门店管理系统.exe"
    
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayName" "${COMPANYNAME} - ${APPNAME} - ${DESCRIPTION}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "UninstallString" "$\\"$INSTDIR\\uninstall.exe$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "InstallLocation" "$\\"$INSTDIR$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayIcon" "$\\"$INSTDIR\\KSX门店管理系统.exe$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
sectionEnd

section "uninstall"
    delete "$INSTDIR\\KSX门店管理系统.exe"
    rmDir /r "$INSTDIR\\playwright-browsers"
    delete "$INSTDIR\\uninstall.exe"
    rmDir "$INSTDIR"
    
    delete "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk"
    rmDir "$SMPROGRAMS\\${APPNAME}"
    delete "$DESKTOP\\${APPNAME}.lnk"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}"
sectionEnd
'''
    
    script_path = Path("installer.nsi")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    return script_path

def create_portable_package():
    """创建便携版压缩包"""
    print("🚀 开始创建便携版压缩包...")
    
    # 检查dist目录
    dist_dir = Path("dist")
    exe_path = dist_dir / "KSX门店管理系统.exe"
    
    if not exe_path.exists():
        print("❌ 找不到应用文件，请先运行 python build_windows.py")
        return False
    
    # 创建临时目录
    temp_dir = Path("temp_portable")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # 复制应用文件
    print("📁 复制应用文件...")
    shutil.copy2(exe_path, temp_dir / "KSX门店管理系统.exe")
    
    # 复制浏览器文件
    playwright_dir = dist_dir / "playwright-browsers"
    if playwright_dir.exists():
        print("📁 复制浏览器文件...")
        shutil.copytree(playwright_dir, temp_dir / "playwright-browsers")
    
    # 创建启动脚本
    start_script = temp_dir / "启动KSX门店管理系统.bat"
    with open(start_script, "w", encoding="utf-8") as f:
        f.write("""@echo off
chcp 65001 >nul
title KSX门店管理系统
echo 🚀 正在启动KSX门店管理系统...
echo.
echo 💡 首次运行时会自动安装Playwright浏览器，请耐心等待
echo.
start "" "KSX门店管理系统.exe"
""")
    
    # 创建说明文件
    readme_file = temp_dir / "使用说明.txt"
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write("""KSX门店管理系统 - 便携版

使用说明：
1. 双击"启动KSX门店管理系统.bat"启动应用
2. 或直接双击"KSX门店管理系统.exe"
3. 首次运行时会自动安装Playwright浏览器，请耐心等待

注意事项：
- 请勿删除playwright-browsers文件夹
- 建议将整个文件夹放在非系统盘
- 如需卸载，直接删除整个文件夹即可

技术支持：
如有问题，请联系技术支持团队。

版本信息：
构建时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
    
    # 创建压缩包
    portable_name = f"KSX门店管理系统_便携版_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    portable_path = dist_dir / portable_name
    
    print("📦 创建便携版压缩包...")
    try:
        with zipfile.ZipFile(portable_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(temp_dir)
                    zipf.write(file_path, arcname)
        
        print(f"✅ 便携版压缩包创建成功: {portable_path}")
        
        # 显示文件大小
        size_mb = portable_path.stat().st_size / (1024 * 1024)
        print(f"📊 压缩包大小: {size_mb:.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建便携版压缩包时出错: {e}")
        return False
    finally:
        # 清理临时目录
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

def main():
    """主函数"""
    print("🚀 开始创建Windows安装包...")
    
    # 检查操作系统
    if platform.system() != "Windows":
        print("❌ 此脚本仅支持Windows系统")
        return False
    
    # 检查dist目录
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ 未找到dist目录，请先运行 python build_windows.py")
        return False
    
    success_count = 0
    
    # 创建便携版压缩包
    if create_portable_package():
        success_count += 1
    
    # 创建NSIS安装包（如果NSIS可用）
    if create_nsis_installer():
        success_count += 1
    
    if success_count > 0:
        print(f"\n🎉 成功创建 {success_count} 个安装包！")
        print("📋 使用说明：")
        print("   1. 便携版：解压后直接运行，无需安装")
        print("   2. 安装版：双击安装包进行安装")
        print("   3. 首次运行时会自动安装Playwright浏览器")
        return True
    else:
        print("\n❌ 安装包创建失败")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
