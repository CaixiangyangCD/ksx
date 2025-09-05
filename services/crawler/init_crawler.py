#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫模块初始化脚本
用于首次设置和依赖安装
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ 错误：需要Python 3.7或更高版本")
        print(f"当前版本：{version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python版本检查通过：{version.major}.{version.minor}.{version.micro}")
    return True


def install_dependencies():
    """安装依赖包"""
    print("\n🔧 正在安装Python依赖包...")
    
    try:
        # 升级pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        print("✅ pip升级完成")
        
        # 安装依赖
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Python依赖包安装完成")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败：{e}")
        return False


def install_playwright_browsers():
    """安装Playwright浏览器"""
    print("\n🌐 正在安装Playwright浏览器...")
    
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                      check=True, capture_output=True)
        print("✅ Playwright浏览器安装完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 浏览器安装失败：{e}")
        return False


def create_directories():
    """创建必要目录"""
    print("\n📁 创建必要目录...")
    
    directories = [
        "screenshots",
        "downloads", 
        "logs",
        "data"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ 创建目录：{directory}")


def create_env_file():
    """创建环境配置文件"""
    print("\n⚙️ 创建环境配置文件...")
    
    env_content = """# KSX爬虫环境配置
# 网站配置
KSX_BASE_URL=https://ksx.dahuafuli.com:8306/
KSX_LOGIN_URL=https://ksx.dahuafuli.com:8306/

# 登录配置
KSX_USERNAME=fsrm001
KSX_PASSWORD=fsrm001

# 浏览器配置
BROWSER_HEADLESS=false
BROWSER_TIMEOUT=30000

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=crawler.log
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ 环境配置文件创建完成")
        return True
    except Exception as e:
        print(f"❌ 环境配置文件创建失败：{e}")
        return False


def test_installation():
    """测试安装是否成功"""
    print("\n🧪 测试安装...")
    
    try:
        # 测试导入
        import playwright
        print("✅ playwright导入成功")
        
        # 测试浏览器启动
        from playwright.async_api import async_playwright
        print("✅ playwright API导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入测试失败：{e}")
        return False


def show_usage():
    """显示使用方法"""
    print("\n" + "="*50)
    print("🎉 爬虫模块初始化完成！")
    print("="*50)
    print("\n📖 使用方法：")
    print("1. 直接运行：python run_crawler.py")
    print("2. 使用批处理：双击 start_crawler.bat")
    print("3. 无头模式：python run_crawler.py --headless")
    print("\n📁 目录结构：")
    print("screenshots/  - 截图保存目录")
    print("downloads/    - 下载文件目录")
    print("logs/         - 日志文件目录")
    print("data/         - 数据保存目录")
    print("\n⚠️  注意事项：")
    print("- 首次运行可能需要较长时间")
    print("- 确保网络连接正常")
    print("- 遵守网站使用条款")
    print("\n🚀 开始使用：")
    print("python run_crawler.py")


def main():
    """主函数"""
    print("🚀 KSX爬虫模块初始化程序")
    print("="*50)
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 安装依赖
    if not install_dependencies():
        return False
    
    # 安装浏览器
    if not install_playwright_browsers():
        return False
    
    # 创建目录
    create_directories()
    
    # 创建环境配置
    create_env_file()
    
    # 测试安装
    if not test_installation():
        return False
    
    # 显示使用方法
    show_usage()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ 初始化完成！")
        else:
            print("\n❌ 初始化失败！")
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 初始化过程出现异常：{e}")
    
    input("\n按回车键退出...")
