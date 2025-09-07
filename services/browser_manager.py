#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器管理器
负责检测、安装和管理Playwright浏览器
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import List, Optional, Dict, Any
from loguru import logger


class BrowserManager:
    """浏览器管理器"""
    
    def __init__(self, project_root: str = None):
        """
        初始化浏览器管理器
        
        Args:
            project_root: 项目根目录，如果为None则自动检测
        """
        if project_root is None:
            # 自动检测项目根目录
            current_file = Path(__file__).resolve()
            self.project_root = current_file.parent.parent
        else:
            self.project_root = Path(project_root)
        
        # 设置浏览器安装路径
        self.browser_path = self.project_root / "playwright-browsers"
        self.browser_path.mkdir(exist_ok=True)
        
        # 设置环境变量
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(self.browser_path)
        
        logger.info(f"浏览器管理器初始化完成，浏览器路径: {self.browser_path}")
    
    def get_system_info(self) -> Dict[str, str]:
        """获取系统信息"""
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "executable": sys.executable
        }
    
    def check_playwright_installation(self) -> bool:
        """检查Playwright是否已安装"""
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
            logger.warning("Playwright未安装")
            return False
    
    def check_browser_installation(self, browser_name: str = "chromium") -> bool:
        """检查指定浏览器是否已安装"""
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                try:
                    if browser_name == "chromium":
                        browser = p.chromium.launch(headless=True)
                    elif browser_name == "firefox":
                        browser = p.firefox.launch(headless=True)
                    elif browser_name == "webkit":
                        browser = p.webkit.launch(headless=True)
                    else:
                        logger.error(f"不支持的浏览器: {browser_name}")
                        return False
                    
                    browser.close()
                    logger.info(f"{browser_name} 浏览器已安装并可正常启动")
                    return True
                except Exception as e:
                    logger.warning(f"{browser_name} 浏览器未安装或无法启动: {e}")
                    return False
        except ImportError:
            logger.error("Playwright未安装，无法检查浏览器")
            return False
    
    def install_playwright(self) -> bool:
        """安装Playwright"""
        try:
            logger.info("开始安装Playwright...")
            
            # 使用uv安装playwright
            result = subprocess.run([
                sys.executable, "-m", "uv", "add", "playwright"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                logger.info("Playwright安装成功")
                return True
            else:
                logger.error(f"Playwright安装失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"安装Playwright时发生错误: {e}")
            return False
    
    def install_browsers(self, browsers: List[str] = None) -> bool:
        """安装Playwright浏览器"""
        if browsers is None:
            browsers = ["chromium"]  # 默认只安装chromium
        
        try:
            logger.info(f"开始安装浏览器: {browsers}")
            
            # 使用playwright install命令安装浏览器
            cmd = [sys.executable, "-m", "playwright", "install"]
            cmd.extend(browsers)
            
            # 设置浏览器安装路径
            env = os.environ.copy()
            env["PLAYWRIGHT_BROWSERS_PATH"] = str(self.browser_path)
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=self.project_root,
                env=env
            )
            
            if result.returncode == 0:
                logger.info(f"浏览器安装成功: {browsers}")
                return True
            else:
                logger.error(f"浏览器安装失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"安装浏览器时发生错误: {e}")
            return False
    
    def setup_environment(self) -> bool:
        """设置完整的浏览器环境"""
        logger.info("开始设置浏览器环境...")
        
        # 1. 检查并安装Playwright
        if not self.check_playwright_installation():
            if not self.install_playwright():
                logger.error("Playwright安装失败")
                return False
        
        # 2. 检查并安装浏览器
        if not self.check_browser_installation("chromium"):
            if not self.install_browsers(["chromium"]):
                logger.error("浏览器安装失败")
                return False
        
        # 3. 验证安装
        if self.check_browser_installation("chromium"):
            logger.info("浏览器环境设置完成")
            return True
        else:
            logger.error("浏览器环境验证失败")
            return False
    
    def get_browser_info(self) -> Dict[str, Any]:
        """获取浏览器信息"""
        info = {
            "system": self.get_system_info(),
            "playwright_installed": self.check_playwright_installation(),
            "browsers": {}
        }
        
        browsers = ["chromium", "firefox", "webkit"]
        for browser in browsers:
            info["browsers"][browser] = self.check_browser_installation(browser)
        
        return info
    
    def cleanup(self):
        """清理资源"""
        # 这里可以添加清理逻辑，比如删除临时文件等
        pass


def setup_browser_environment(project_root: str = None) -> bool:
    """
    设置浏览器环境的便捷函数
    
    Args:
        project_root: 项目根目录
        
    Returns:
        bool: 设置是否成功
    """
    manager = BrowserManager(project_root)
    try:
        return manager.setup_environment()
    finally:
        manager.cleanup()


if __name__ == "__main__":
    # 测试浏览器管理器
    manager = BrowserManager()
    
    print("=== 系统信息 ===")
    system_info = manager.get_system_info()
    for key, value in system_info.items():
        print(f"{key}: {value}")
    
    print("\n=== 浏览器信息 ===")
    browser_info = manager.get_browser_info()
    print(f"Playwright已安装: {browser_info['playwright_installed']}")
    for browser, installed in browser_info['browsers'].items():
        print(f"{browser}: {'已安装' if installed else '未安装'}")
    
    print("\n=== 设置浏览器环境 ===")
    success = manager.setup_environment()
    print(f"设置结果: {'成功' if success else '失败'}")
