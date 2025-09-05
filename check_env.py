#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境检查脚本
检查运行KSX门店管理系统所需的环境依赖
"""

import sys
import subprocess
import platform
import os

def print_header():
    """打印标题"""
    print("=" * 60)
    print("KSX门店管理系统 - 环境检查")
    print("=" * 60)
    print()

def check_python():
    """检查Python环境"""
    print("🐍 Python环境检查:")
    print(f"   Python版本: {platform.python_version()}")
    print(f"   Python路径: {sys.executable}")
    print(f"   操作系统: {platform.system()} {platform.release()}")
    
    # 检查Python版本兼容性
    version = platform.python_version_tuple()
    major, minor = int(version[0]), int(version[1])
    
    if major == 3 and 7 <= minor <= 11:
        print("   ✓ Python版本兼容")
    elif major == 3 and minor >= 12:
        print("   ⚠️  Python 3.12+ 可能与PySide6-WebEngine不兼容")
        print("   建议使用Python 3.11或使用简化版桌面应用")
    else:
        print("   ✗ Python版本过低，需要Python 3.7+")
    
    print()
    return True

def check_nodejs():
    """检查Node.js环境"""
    print("🟢 Node.js环境检查:")
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, check=True)
        node_version = result.stdout.strip()
        print(f"   Node.js版本: {node_version}")
        
        result = subprocess.run(['npm', '--version'], 
                              capture_output=True, text=True, check=True)
        npm_version = result.stdout.strip()
        print(f"   npm版本: {npm_version}")
        
        print("   ✓ Node.js环境正常")
        print()
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ✗ Node.js未安装或版本过低")
        print("   请访问 https://nodejs.org 下载安装Node.js 16+")
        print()
        return False

def check_python_packages():
    """检查Python包"""
    print("📦 Python包检查:")
    
    packages = [
        ('PySide6', 'PySide6'),
        ('PySide6-WebEngine', 'PySide6.QtWebEngineWidgets')
    ]
    
    all_installed = True
    webengine_available = False
    
    for package_name, import_name in packages:
        try:
            __import__(import_name)
            print(f"   ✓ {package_name} 已安装")
            if 'WebEngine' in package_name:
                webengine_available = True
        except ImportError:
            print(f"   ✗ {package_name} 未安装")
            all_installed = False
    
    if not all_installed:
        print("   请运行: pip install -r requirements.txt")
        if not webengine_available:
            print("   或者使用简化版: pip install -r requirements_simple.txt")
    
    print()
    return all_installed, webengine_available

def check_project_files():
    """检查项目文件"""
    print("📁 项目文件检查:")
    
    required_files = [
        'package.json',
        'vite.config.ts',
        'src/main.ts',
        'src/App.vue'
    ]
    
    desktop_files = [
        'desktop_app.py',
        'desktop_app_simple.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✓ {file_path}")
        else:
            print(f"   ✗ {file_path} 缺失")
            all_exist = False
    
    print("\n   桌面应用文件:")
    desktop_available = False
    for file_path in desktop_files:
        if os.path.exists(file_path):
            print(f"   ✓ {file_path}")
            desktop_available = True
        else:
            print(f"   ✗ {file_path} 缺失")
    
    print()
    return all_exist, desktop_available

def check_node_modules():
    """检查Node.js依赖"""
    print("📚 Node.js依赖检查:")
    
    if os.path.exists('node_modules'):
        print("   ✓ node_modules目录存在")
        print("   ✓ 依赖已安装")
    else:
        print("   ✗ node_modules目录不存在")
        print("   请运行: npm install")
    
    print()

def provide_recommendations(webengine_available, desktop_available):
    """提供建议"""
    print("💡 使用建议:")
    print()
    
    print("1. 仅使用Web版本:")
    print("   运行: start_web_only.bat")
    print("   或: npm run dev")
    print()
    
    if webengine_available and desktop_available:
        print("2. 使用完整桌面版本:")
        print("   运行: start_desktop.bat")
        print("   或: python desktop_app.py")
        print()
    elif desktop_available:
        print("2. 使用简化桌面版本:")
        print("   运行: start_simple_desktop.bat")
        print("   或: python desktop_app_simple.py")
        print()
    
    print("3. 安装依赖:")
    if webengine_available:
        print("   pip install -r requirements.txt # 完整版依赖")
    else:
        print("   pip install -r requirements_simple.txt # 简化版依赖")
    print("   npm install                        # Node.js依赖")
    print()
    
    if not webengine_available:
        print("⚠️  注意: PySide6-WebEngine不可用，建议使用简化版桌面应用")
        print("   简化版功能: 启动Web服务器 + 自动打开浏览器")
        print()

def main():
    """主函数"""
    print_header()
    
    # 执行各项检查
    python_ok = check_python()
    nodejs_ok = check_nodejs()
    python_packages_ok, webengine_available = check_python_packages()
    project_files_ok, desktop_available = check_project_files()
    check_node_modules()
    
    # 总结
    print("📊 检查总结:")
    if all([python_ok, nodejs_ok, python_packages_ok, project_files_ok]):
        print("   🎉 环境检查通过！可以正常运行系统")
    else:
        print("   ⚠️  环境检查未完全通过，请根据上述提示安装缺失的依赖")
    
    print()
    provide_recommendations(webengine_available, desktop_available)
    
    # 等待用户确认
    input("按回车键退出...")

if __name__ == "__main__":
    main()
