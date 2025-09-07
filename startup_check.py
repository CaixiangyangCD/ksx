#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动检查脚本
在应用启动时自动检查和安装必要的组件
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from loguru import logger


def get_app_root():
    """获取应用根目录"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的应用
        return Path(sys.executable).parent
    else:
        # 如果是开发环境
        return Path(__file__).parent


def check_python_environment():
    """检查Python环境"""
    logger.info("检查Python环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version < (3, 8):
        logger.error(f"Python版本过低: {python_version.major}.{python_version.minor}，需要3.8+")
        return False
    
    logger.info(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    return True


def check_and_install_playwright():
    """检查并安装Playwright"""
    logger.info("检查Playwright...")
    
    try:
        import playwright
        # 尝试获取版本信息
        try:
            version = playwright.__version__
        except AttributeError:
            version = "未知版本"
        logger.info(f"Playwright已安装，版本: {version}")
        return True
    except ImportError:
        logger.info("Playwright未安装，正在安装...")
        
        try:
            # 使用uv安装playwright
            result = subprocess.run([
                sys.executable, "-m", "uv", "add", "playwright"
            ], capture_output=True, text=True, cwd=get_app_root())
            
            if result.returncode == 0:
                logger.info("Playwright安装成功")
                return True
            else:
                logger.error(f"Playwright安装失败: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"安装Playwright时发生错误: {e}")
            return False


def check_and_install_browsers():
    """检查并安装浏览器"""
    logger.info("检查浏览器...")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            try:
                # 尝试启动chromium
                browser = p.chromium.launch(headless=True)
                browser.close()
                logger.info("Chromium浏览器已安装")
                return True
            except Exception as e:
                logger.info(f"浏览器未安装，正在安装: {e}")
                
                # 安装chromium
                result = subprocess.run([
                    sys.executable, "-m", "playwright", "install", "chromium"
                ], capture_output=True, text=True, cwd=get_app_root())
                
                if result.returncode == 0:
                    logger.info("浏览器安装成功")
                    return True
                else:
                    logger.error(f"浏览器安装失败: {result.stderr}")
                    return False
    except Exception as e:
        logger.error(f"检查浏览器时发生错误: {e}")
        return False


def check_dependencies():
    """检查其他依赖"""
    logger.info("检查其他依赖...")
    
    required_modules = [
        "fastapi",
        "uvicorn", 
        "loguru",
        "PySide6",
        "openpyxl",
        "pandas"
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            logger.info(f"✓ {module}")
        except ImportError:
            missing_modules.append(module)
            logger.warning(f"✗ {module}")
    
    if missing_modules:
        logger.error(f"缺少依赖: {missing_modules}")
        return False
    
    logger.info("所有依赖检查完成")
    return True


def setup_environment():
    """设置环境变量"""
    logger.info("设置环境变量...")
    
    app_root = get_app_root()
    
    # 设置浏览器路径
    browser_path = app_root / "playwright-browsers"
    browser_path.mkdir(exist_ok=True)
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browser_path)
    
    # 设置其他环境变量
    os.environ["PYTHONPATH"] = str(app_root)
    
    logger.info(f"浏览器路径设置为: {browser_path}")
    return True


def perform_startup_check():
    """执行启动检查"""
    logger.info("开始启动检查...")
    
    checks = [
        ("Python环境", check_python_environment),
        ("Playwright", check_and_install_playwright),
        ("浏览器", check_and_install_browsers),
        ("其他依赖", check_dependencies),
        ("环境变量", setup_environment),
    ]
    
    for check_name, check_func in checks:
        logger.info(f"检查: {check_name}")
        if not check_func():
            logger.error(f"启动检查失败: {check_name}")
            return False
        logger.info(f"✓ {check_name} 检查通过")
    
    logger.info("🎉 所有启动检查通过！")
    return True


def main():
    """主函数"""
    # 配置日志
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # 执行启动检查
    if perform_startup_check():
        logger.info("启动检查完成，可以启动应用")
        return True
    else:
        logger.error("启动检查失败，请检查错误信息")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
