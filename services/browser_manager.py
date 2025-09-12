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
            if getattr(sys, 'frozen', False):
                # 打包环境：直接使用用户目录
                user_home = Path.home()
                self.project_root = user_home / "KSX_App"
                self.project_root.mkdir(exist_ok=True)
                logger.info(f" 浏览器管理器：打包环境，使用用户目录: {self.project_root}")
            else:
                # 检查是否在临时目录中运行（爬虫子进程）
                current_path = str(Path(__file__).resolve())
                if 'Temp' in current_path and '_MEI' in current_path:
                    # 在临时目录中运行，使用用户目录
                    user_home = Path.home()
                    self.project_root = user_home / "KSX_App"
                    self.project_root.mkdir(exist_ok=True)
                    logger.info(f" 浏览器管理器：临时目录环境，强制使用用户目录: {self.project_root}")
                else:
                    # 开发环境：使用项目根目录
                    current_file = Path(__file__).resolve()
                    self.project_root = current_file.parent.parent
                    logger.info(f" 浏览器管理器：开发环境，使用项目根目录: {self.project_root}")
        else:
            self.project_root = Path(project_root)
        
        # 设置浏览器安装路径
        self.browser_path = self.project_root / "playwright-browsers"
        self.browser_path.mkdir(exist_ok=True)
        
        # 设置环境变量
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(self.browser_path)
        
        logger.info(f"浏览器管理器初始化完成，浏览器路径: {self.browser_path}")
        logger.info(f" 浏览器管理器：设置PLAYWRIGHT_BROWSERS_PATH环境变量: {self.browser_path}")
        logger.info(f" 浏览器管理器：当前环境变量值: {os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '未设置')}")
    
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
            # 检查浏览器文件是否存在，而不是启动浏览器
            # 这样可以避免在异步环境中的同步API冲突
            import asyncio
            
            # 检查是否在异步环境中
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    logger.warning("在异步环境中跳过浏览器启动检查，仅检查文件存在性")
                    return self._check_browser_files(browser_name)
            except RuntimeError:
                # 没有运行中的事件循环，可以使用同步API
                pass
            
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
    
    def _check_browser_files(self, browser_name: str) -> bool:
        """检查浏览器文件是否存在（不启动浏览器）"""
        try:
            # 使用浏览器管理器的浏览器路径
            browser_path = self.browser_path
            
            if browser_name == "chromium":
                # 检查 Chromium 可执行文件
                chromium_dirs = list(browser_path.glob('chromium-*'))
                if chromium_dirs:
                    for chromium_dir in chromium_dirs:
                        chrome_exe = chromium_dir / 'chrome-win' / 'chrome.exe'
                        if chrome_exe.exists():
                            logger.info(f"找到chromium浏览器: {chrome_exe}")
                            return True
                        chrome_exe_alt = chromium_dir / 'chrome-win' / 'chrome'
                        if chrome_exe_alt.exists():
                            logger.info(f"找到chromium浏览器: {chrome_exe_alt}")
                            return True
                logger.warning(f"未找到chromium浏览器可执行文件，检查路径: {browser_path}")
                return False
            elif browser_name == "firefox":
                firefox_paths = [
                    browser_path / 'firefox-*' / 'firefox' / 'firefox.exe',
                    browser_path / 'firefox-*' / 'firefox' / 'firefox',
                ]
                for path_pattern in firefox_paths:
                    if list(browser_path.glob('firefox-*')):
                        return True
            elif browser_name == "webkit":
                webkit_paths = [
                    browser_path / 'webkit-*' / 'pw_run.sh',
                    browser_path / 'webkit-*' / 'Playwright.app',
                ]
                for path_pattern in webkit_paths:
                    if list(browser_path.glob('webkit-*')):
                        return True
            
            logger.info(f"{browser_name} 浏览器文件检查完成")
            return True  # 假设文件存在，让实际运行时处理错误
        except Exception as e:
            logger.warning(f"检查 {browser_name} 浏览器文件时出错: {e}")
            return True  # 假设存在，让实际运行时处理
    
    def _copy_packaged_browser(self) -> bool:
        """从打包的浏览器目录复制到用户目录"""
        try:
            import sys
            import shutil
            
            # 检查是否在打包环境中
            if not getattr(sys, 'frozen', False):
                logger.info("非打包环境，跳过浏览器复制")
                return False
            
            # 获取打包的浏览器路径
            packaged_browser_path = Path(sys._MEIPASS) / 'playwright-browsers'
            if not packaged_browser_path.exists():
                logger.warning(f"打包的浏览器目录不存在: {packaged_browser_path}")
                return False
            
            # 确保用户目录存在
            user_browser_path = self.browser_path
            user_browser_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"开始复制浏览器从 {packaged_browser_path} 到 {user_browser_path}")
            
            # 复制整个浏览器目录
            for item in packaged_browser_path.iterdir():
                dest_item = user_browser_path / item.name
                if dest_item.exists():
                    logger.info(f"目标已存在，跳过: {dest_item}")
                    continue
                
                if item.is_dir():
                    logger.info(f"复制目录: {item.name}")
                    shutil.copytree(item, dest_item)
                else:
                    logger.info(f"复制文件: {item.name}")
                    shutil.copy2(item, dest_item)
            
            logger.info("浏览器复制完成")
            return True
            
        except Exception as e:
            logger.error(f"复制浏览器时发生错误: {e}")
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
            browsers = ["chromium"]  # 使用chromium版本
        
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
        
        # 2. 检查是否在异步环境中
        try:
            import asyncio
            loop = asyncio.get_running_loop()
            if loop.is_running():
                logger.warning("在异步环境中，需要安装浏览器但无法验证启动")
                # 在异步环境中，检查文件是否存在
                if not self._check_browser_files("chromium"):
                    logger.warning("chromium 浏览器文件不存在，尝试从打包的浏览器复制")
                    # 尝试从打包的浏览器目录复制到用户目录
                    if self._copy_packaged_browser():
                        logger.info("成功从打包文件复制浏览器到用户目录")
                        return True
                    else:
                        logger.warning("复制浏览器失败，将在实际使用时处理")
                        return True  # 返回True，让爬虫启动时处理
                
                # 浏览器文件存在
                logger.info("chromium 浏览器已存在（异步环境）")
                return True
        except RuntimeError:
            # 没有运行中的事件循环，可以正常执行
            pass
        
        # 3. 检查并安装浏览器（仅在非异步环境中）
        if not self.check_browser_installation("chromium"):
            if not self.install_browsers(["chromium"]):
                logger.error("浏览器安装失败")
                return False
        
        # 4. 验证安装
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
