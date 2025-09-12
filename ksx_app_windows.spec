# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# 获取项目根目录
import os
project_root = Path(os.getcwd()).absolute()

# 构建数据文件路径
frontend_dist = project_root / 'frontend' / 'dist'
database_dir = project_root / 'database'
services_dir = project_root / 'services'
backend_dir = project_root / 'backend'
desktop_dir = project_root / 'desktop'
playwright_installer = project_root / 'services' / 'playwright_installer.py'

# Playwright浏览器路径
import os
# 使用项目目录中预安装的浏览器
playwright_browsers = project_root / 'playwright-browsers'

# 检查路径是否存在并转换为字符串
datas = []
if frontend_dist.exists():
    datas.append((str(frontend_dist), 'frontend/dist'))
if database_dir.exists():
    datas.append((str(database_dir), 'database'))
if services_dir.exists():
    datas.append((str(services_dir), 'services'))
if backend_dir.exists():
    datas.append((str(backend_dir), 'backend'))
if desktop_dir.exists():
    datas.append((str(desktop_dir), 'desktop'))
if playwright_installer.exists():
    datas.append((str(playwright_installer), 'services'))
if playwright_browsers.exists():
    datas.append((str(playwright_browsers), 'playwright-browsers'))
    print(f"Added preinstalled browsers: {playwright_browsers}")

# 添加SQLite3 DLL文件 - 从项目根目录
sqlite3_dll_path = project_root / '_sqlite3.pyd'
if sqlite3_dll_path.exists():
    datas.append((str(sqlite3_dll_path), '.'))
    print(f"Added _sqlite3.pyd: {sqlite3_dll_path}")
    
# 添加SQLite3相关文件
sqlite3_dll = project_root / 'sqlite3.dll'
if sqlite3_dll.exists():
    datas.append((str(sqlite3_dll), '.'))
    print(f"Added sqlite3.dll: {sqlite3_dll}")

a = Analysis(
    ['desktop/ksx_desktop_app_windows.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'uvicorn', 'fastapi', 'loguru', 'sqlite3', 'pandas', 'openpyxl', 
        'numpy', 'numpy.core', 'numpy.core._methods', 'numpy.lib.format',
        'playwright', 'playwright.async_api', 'playwright._impl', 
        'playwright._impl._browser_type', 'playwright._impl._browser', 
        'playwright._impl._browser_context', 'playwright._impl._page', 
        'playwright._impl._element_handle', 'playwright._impl._locator', 
        'playwright._impl._network', 'playwright._impl._cdp_session', 
        'playwright._impl._js_handle', 'playwright._impl._worker', 
        'playwright._impl._frame', 'playwright._impl._route', 
        'playwright._impl._request', 'playwright._impl._response', 
        'playwright._impl._console_message', 'playwright._impl._dialog', 
        'playwright._impl._download', 'playwright._impl._file_chooser', 
        'playwright._impl._accessibility', 'playwright._impl._video', 
        'playwright._impl._tracing', 'playwright._impl._coverage', 
        'playwright._impl._har', 'playwright._impl._api_request', 
        'playwright._impl._api_response', 'playwright._impl._expect', 
        'requests', 'beautifulsoup4', 'lxml', 'PIL', 'PIL.Image',
        'PySide6.QtCore', 'PySide6.QtWidgets', 'PySide6.QtGui',
        'PySide6.QtWebEngineWidgets', 'PySide6.QtWebEngineCore',
        'http.server', 'socketserver', 'threading', 'multiprocessing',
        'pkg_resources', 'pkg_resources.py2_warn'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'matplotlib', 'scipy', 'IPython', 'jupyter', 'pytest', 
        'sphinx', 'tensorflow', 'torch', 'sklearn'
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='KSX门店管理系统',
    debug=True,  # 启用调试模式
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 禁用UPX压缩，避免兼容性问题
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以在这里指定图标文件路径
    version="version_info.txt",  # 版本信息文件
)
