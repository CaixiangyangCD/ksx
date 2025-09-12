#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playwright安装和检查工具
用于在打包后的应用中自动安装和配置Playwright
"""

import os
import sys
import subprocess

def get_project_root():
    """获取项目根目录"""
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的情况
        return os.path.dirname(sys.executable)
    else:
        # 开发环境
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_playwright_installation():
    """检查Playwright是否已安装"""
    try:
        import importlib.util
        spec = importlib.util.find_spec("playwright")
        if spec is not None:
            # print("✓ Playwright模块已安装")
            return True
        else:
            # print("✗ Playwright模块未安装")
            return False
    except Exception:
        # print("✗ Playwright模块未安装")
        return False

def install_playwright():
    """安装Playwright"""
    try:
        # print("正在安装Playwright...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "playwright"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            # print("✓ Playwright安装成功")
            return True
        else:
            # print(f"✗ Playwright安装失败: {result.stderr}")
            return False
    except Exception as e:
        # print(f"✗ Playwright安装异常: {e}")
        return False

def install_playwright_browsers():
    """安装Playwright浏览器"""
    try:
        # print("正在安装Playwright浏览器...")
        
        # 设置浏览器安装路径
        project_root = get_project_root()
        browser_path = os.path.join(project_root, "playwright-browsers")
        os.makedirs(browser_path, exist_ok=True)
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browser_path
        
        # 安装Chromium浏览器
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium"
        ], capture_output=True, text=True, timeout=600, env=os.environ.copy())
        
        if result.returncode == 0:
            # print("✓ Playwright浏览器安装成功")
            return True
        else:
            # print(f"✗ Playwright浏览器安装失败: {result.stderr}")
            return False
    except Exception as e:
        # print(f"✗ Playwright浏览器安装异常: {e}")
        return False

def setup_playwright_environment():
    """设置Playwright环境"""
    try:
        project_root = get_project_root()
        browser_path = os.path.join(project_root, "playwright-browsers")
        
        # 确保浏览器目录存在
        os.makedirs(browser_path, exist_ok=True)
        
        # 设置环境变量
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browser_path
        
        # print(f"✓ Playwright环境已设置，浏览器路径: {browser_path}")
        return True
    except Exception as e:
        # print(f"✗ Playwright环境设置失败: {e}")
        return False

def ensure_playwright_ready():
    """确保Playwright已准备就绪"""
    # print(" 检查Playwright环境...")
    
    # 1. 检查Playwright模块
    if not check_playwright_installation():
        # print(" 正在安装Playwright模块...")
        if not install_playwright():
            return False
    
    # 2. 设置环境
    if not setup_playwright_environment():
        return False
    
    # 3. 检查浏览器
    project_root = get_project_root()
    browser_path = os.path.join(project_root, "playwright-browsers")
    chromium_path = os.path.join(browser_path, "chromium-1091", "chrome-mac", "Chromium.app")
    
    if not os.path.exists(chromium_path):
        # print(" 正在安装Playwright浏览器...")
        if not install_playwright_browsers():
            return False
    
    # 4. 测试Playwright
    try:
        import importlib.util
        spec = importlib.util.find_spec("playwright.async_api")
        if spec is not None:
            # print("✓ Playwright测试成功")
            return True
        else:
            # print("✗ Playwright测试失败")
            return False
    except Exception as e:
        # print(f"✗ Playwright测试失败: {e}")
        return False

def main():
    """主函数"""
    # print(" Playwright环境检查和安装工具")
    # print("=" * 50)
    
    if ensure_playwright_ready():
        # print("\n Playwright环境准备完成！")
        return True
    else:
        # print("\n❌ Playwright环境准备失败！")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
