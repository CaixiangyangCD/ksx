#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包功能测试脚本
"""

import os
import sys
import subprocess
from pathlib import Path


def test_browser_manager():
    """测试浏览器管理器"""
    print("🧪 测试浏览器管理器...")
    
    try:
        from services.browser_manager import BrowserManager
        
        manager = BrowserManager()
        
        # 测试系统信息获取
        system_info = manager.get_system_info()
        print(f"✓ 系统信息: {system_info['platform']} {system_info['architecture']}")
        
        # 测试Playwright检查
        playwright_installed = manager.check_playwright_installation()
        print(f"✓ Playwright检查: {'已安装' if playwright_installed else '未安装'}")
        
        # 测试浏览器检查
        browser_installed = manager.check_browser_installation("chromium")
        print(f"✓ 浏览器检查: {'已安装' if browser_installed else '未安装'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 浏览器管理器测试失败: {e}")
        return False


def test_startup_check():
    """测试启动检查"""
    print("🧪 测试启动检查...")
    
    try:
        result = subprocess.run([
            sys.executable, "startup_check.py"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✓ 启动检查测试通过")
            return True
        else:
            print(f"❌ 启动检查测试失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 启动检查测试失败: {e}")
        return False


def test_desktop_app():
    """测试桌面应用启动"""
    print("🧪 测试桌面应用...")
    
    try:
        # 这里只是检查导入是否正常，不实际启动GUI
        import desktop.ksx_desktop_app
        print("✓ 桌面应用模块导入成功")
        return True
        
    except Exception as e:
        print(f"❌ 桌面应用测试失败: {e}")
        return False


def test_crawler():
    """测试爬虫模块"""
    print("🧪 测试爬虫模块...")
    
    try:
        from services.crawler.crawler import KSXCrawler
        print("✓ 爬虫模块导入成功")
        return True
        
    except Exception as e:
        print(f"❌ 爬虫模块测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始打包功能测试...\n")
    
    tests = [
        ("浏览器管理器", test_browser_manager),
        ("启动检查", test_startup_check),
        ("桌面应用", test_desktop_app),
        ("爬虫模块", test_crawler),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} 测试失败")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！可以开始打包。")
        return True
    else:
        print("⚠️ 部分测试失败，请检查问题后再进行打包。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


