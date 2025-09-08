# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['desktop/ksx_desktop_app.py'],
    pathex=[],
    binaries=[],
    datas=[('/Users/xiangyang/Code/Personal/ksx/frontend/dist', 'frontend/dist'), ('/Users/xiangyang/Code/Personal/ksx/database', 'database'), ('/Users/xiangyang/Code/Personal/ksx/services', 'services'), ('/Users/xiangyang/Code/Personal/ksx/backend', 'backend'), ('/Users/xiangyang/Code/Personal/ksx/desktop', 'desktop'), ('/Users/xiangyang/Code/Personal/ksx/services/playwright_installer.py', 'services')],
    hiddenimports=['uvicorn', 'fastapi', 'loguru', 'sqlite3', 'pandas', 'openpyxl', 'playwright', 'playwright.async_api', 'playwright._impl', 'playwright._impl._browser_type', 'playwright._impl._browser', 'playwright._impl._browser_context', 'playwright._impl._page', 'playwright._impl._element_handle', 'playwright._impl._locator', 'playwright._impl._network', 'playwright._impl._cdp_session', 'playwright._impl._js_handle', 'playwright._impl._worker', 'playwright._impl._frame', 'playwright._impl._route', 'playwright._impl._request', 'playwright._impl._response', 'playwright._impl._console_message', 'playwright._impl._dialog', 'playwright._impl._download', 'playwright._impl._file_chooser', 'playwright._impl._accessibility', 'playwright._impl._video', 'playwright._impl._tracing', 'playwright._impl._coverage', 'playwright._impl._har', 'playwright._impl._api_request', 'playwright._impl._api_response', 'playwright._impl._expect', 'requests', 'beautifulsoup4', 'lxml'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'IPython', 'jupyter', 'pytest', 'sphinx'],
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
)
app = BUNDLE(
    exe,
    name='KSX门店管理系统.app',
    icon=None,
    bundle_identifier=None,
)
