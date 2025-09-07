# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# 项目根目录
project_root = Path(r'/Users/xiangyang/Code/Personal/ksx')

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
    hooksconfig={},
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
    info_plist={
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
    },
)
