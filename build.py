#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KSX应用打包脚本
支持Windows和macOS平台的exe和app打包
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from typing import List, Dict, Any


class AppBuilder:
    """应用打包器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.platform = platform.system().lower()
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        
    def clean_build_dirs(self):
        """清理构建目录"""
        print("🧹 清理构建目录...")
        for dir_path in [self.build_dir, self.dist_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
            dir_path.mkdir(exist_ok=True)
    
    def build_frontend(self):
        """构建前端"""
        print("🏗️ 构建前端项目...")
        frontend_dir = self.project_root / "frontend"
        
        # 安装前端依赖
        subprocess.run(["pnpm", "install"], cwd=frontend_dir, check=True)
        
        # 构建前端
        subprocess.run(["pnpm", "run", "build"], cwd=frontend_dir, check=True)
        
        print("✅ 前端构建完成")
    
    def prepare_python_dependencies(self):
        """准备Python依赖"""
        print("📦 准备Python依赖...")
        
        # 使用uv导出依赖
        requirements_file = self.project_root / "requirements.txt"
        subprocess.run([
            "uv", "export", "--format", "requirements-txt",
            "--output-file", str(requirements_file)
        ], cwd=self.project_root, check=True)
        
        print("✅ Python依赖准备完成")
    
    def create_spec_file(self) -> Path:
        """创建PyInstaller spec文件"""
        print("📝 创建PyInstaller spec文件...")
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# 项目根目录
project_root = Path(r'{self.project_root}')

# 数据文件
datas = [
    (str(project_root / "frontend" / "dist"), "frontend/dist"),
    (str(project_root / "database"), "database"),
    (str(project_root / "services"), "services"),
    (str(project_root / "backend"), "backend"),
    (str(project_root / "desktop"), "desktop"),
    (str(project_root / "startup_check.py"), "."),
    (str(project_root / "services" / "browser_manager.py"), "services"),
]

# 排除Playwright浏览器文件，让应用在运行时动态安装
excludes = [
    'playwright._impl._browser_type',
    'playwright._impl._browser',
    'playwright._impl._browser_context',
    'playwright._impl._page',
]

# 隐藏导入
hiddenimports = [
    "PySide6.QtCore",
    "PySide6.QtGui", 
    "PySide6.QtWidgets",
    "PySide6.QtWebEngineWidgets",
    "PySide6.QtWebEngineCore",
    "fastapi",
    "uvicorn",
    "loguru",
    "playwright",
    "playwright.async_api",
    "openpyxl",
    "pandas",
    "PIL",
    "sqlite3",
    "asyncio",
    "json",
    "csv",
    "datetime",
    "pathlib",
    "typing",
    "subprocess",
    "platform",
    "shutil",
    "requests",
    "beautifulsoup4",
    "lxml",
]

# 排除模块
excludes = [
    "tkinter",
    "matplotlib",
    "numpy.distutils",
    "scipy",
    "IPython",
    "jupyter",
    "notebook",
    "pytest",
    "sphinx",
]

# 主程序
a = Analysis(
    ['desktop/ksx_desktop_app.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KSX门店管理系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / "assets" / "icon.ico") if (project_root / "assets" / "icon.ico").exists() else None,
)

# 创建macOS app bundle
app = BUNDLE(
    exe,
    name='KSX门店管理系统.app',
    icon=str(project_root / "assets" / "icon.icns") if (project_root / "assets" / "icon.icns").exists() else None,
    bundle_identifier='com.ksx.store-management',
    info_plist={{
        'CFBundleName': 'KSX门店管理系统',
        'CFBundleDisplayName': 'KSX门店管理系统',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleExecutable': 'KSX门店管理系统',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': 'KSX ',
        'LSMinimumSystemVersion': '10.15.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
    }},
)
'''
        
        spec_file = self.project_root / "ksx_app.spec"
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print("✅ Spec文件创建完成")
        return spec_file
    
    def build_with_pyinstaller(self, spec_file: Path):
        """使用PyInstaller构建应用"""
        print("🔨 使用PyInstaller构建应用...")
        
        # 安装PyInstaller
        subprocess.run([
            "uv", "add", "pyinstaller"
        ], cwd=self.project_root, check=True)
        
        # 构建应用
        env = os.environ.copy()
        env["PYINSTALLER_DISABLE_CODESIGN"] = "1"
        
        subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            str(spec_file)
        ], cwd=self.project_root, env=env, check=True)
        
        print("✅ PyInstaller构建完成")
    
    def create_installer_script(self):
        """创建安装脚本"""
        print("📋 创建安装脚本...")
        
        if self.platform == "windows":
            self.create_windows_installer()
        elif self.platform == "darwin":
            self.create_macos_installer()
        else:
            print(f"⚠️ 不支持的操作系统: {self.platform}")
    
    def create_windows_installer(self):
        """创建Windows安装脚本"""
        installer_script = self.project_root / "install_windows.bat"
        
        script_content = '''@echo off
echo 正在安装KSX门店管理系统...

REM 检查是否已安装
if exist "%PROGRAMFILES%\\KSX门店管理系统\\KSX门店管理系统.exe" (
    echo 检测到已安装的版本，正在卸载...
    "%PROGRAMFILES%\\KSX门店管理系统\\uninstall.exe" /S
)

REM 创建安装目录
mkdir "%PROGRAMFILES%\\KSX门店管理系统" 2>nul

REM 复制文件
xcopy /E /I /Y "dist\\KSX门店管理系统\\*" "%PROGRAMFILES%\\KSX门店管理系统\\"

REM 创建桌面快捷方式
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\KSX门店管理系统.lnk'); $Shortcut.TargetPath = '%PROGRAMFILES%\\KSX门店管理系统\\KSX门店管理系统.exe'; $Shortcut.Save()"

REM 创建开始菜单快捷方式
mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\KSX门店管理系统" 2>nul
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\KSX门店管理系统\\KSX门店管理系统.lnk'); $Shortcut.TargetPath = '%PROGRAMFILES%\\KSX门店管理系统\\KSX门店管理系统.exe'; $Shortcut.Save()"

echo 安装完成！
pause
'''
        
        with open(installer_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print("✅ Windows安装脚本创建完成")
    
    def create_macos_installer(self):
        """创建macOS安装脚本"""
        installer_script = self.project_root / "install_macos.sh"
        
        script_content = '''#!/bin/bash

echo "正在安装KSX门店管理系统..."

# 检查是否已安装
if [ -d "/Applications/KSX门店管理系统.app" ]; then
    echo "检测到已安装的版本，正在卸载..."
    rm -rf "/Applications/KSX门店管理系统.app"
fi

# 复制应用到Applications目录
cp -R "dist/KSX门店管理系统.app" "/Applications/"

# 设置权限
chmod +x "/Applications/KSX门店管理系统.app/Contents/MacOS/KSX门店管理系统"

echo "安装完成！"
echo "您可以在Applications文件夹中找到KSX门店管理系统"
'''
        
        with open(installer_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 设置执行权限
        os.chmod(installer_script, 0o755)
        
        print("✅ macOS安装脚本创建完成")
    
    def build(self):
        """执行完整的构建流程"""
        print(f"🚀 开始构建KSX应用 (平台: {self.platform})")
        
        try:
            # 1. 清理构建目录
            self.clean_build_dirs()
            
            # 2. 构建前端
            self.build_frontend()
            
            # 3. 准备Python依赖
            self.prepare_python_dependencies()
            
            # 4. 创建spec文件
            spec_file = self.create_spec_file()
            
            # 5. 使用PyInstaller构建
            self.build_with_pyinstaller(spec_file)
            
            # 6. 创建安装脚本
            self.create_installer_script()
            
            print("🎉 构建完成！")
            print(f"📁 输出目录: {self.dist_dir}")
            
            if self.platform == "windows":
                print("💿 可执行文件: dist/KSX门店管理系统/KSX门店管理系统.exe")
                print("📋 安装脚本: install_windows.bat")
            elif self.platform == "darwin":
                print("💿 应用程序: dist/KSX门店管理系统.app")
                print("📋 安装脚本: install_macos.sh")
            
        except Exception as e:
            print(f"❌ 构建失败: {e}")
            sys.exit(1)


def main():
    """主函数"""
    builder = AppBuilder()
    builder.build()


if __name__ == "__main__":
    main()
