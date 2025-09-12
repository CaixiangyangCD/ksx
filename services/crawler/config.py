#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫配置文件
"""

import os
from typing import Dict, Any

# 网站配置
WEBSITE_CONFIG = {
    'base_url': 'https://ksx.dahuafuli.com:8306/',
    'login_url': 'https://ksx.dahuafuli.com:8306/',
    'timeout': 30000,  # 毫秒
}

# 登录配置
LOGIN_CONFIG = {
    'username': 'fsrm001',
    'password': 'fsrm001',
    'username_field': 'input[name="userId"]',
    'password_field': 'input[name="pass"]',
    'submit_button': 'button[type="submit"]',
}

# 浏览器配置
BROWSER_CONFIG = {
    'headless': True,   # 是否无头模式
    'browser_path': '../playwright-config/browsers',  # 自定义浏览器安装路径
    'viewport': {
        'width': 1920,
        'height': 1080
    },
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'args': [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--disable-gpu'
    ]
}

# 日志配置
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'crawler.log',
    'encoding': 'utf-8'
}

# 文件路径配置
PATH_CONFIG = {
    'screenshots': '../playwright-config/screenshots',
    'downloads': '../playwright-config/downloads',
    'logs': 'logs',
    'data': 'data'
}

# 创建必要的目录
def create_directories():
    """创建必要的目录"""
    for path in PATH_CONFIG.values():
        os.makedirs(path, exist_ok=True)

# 获取配置
def get_config() -> Dict[str, Any]:
    """获取完整配置"""
    return {
        'website': WEBSITE_CONFIG,
        'login': LOGIN_CONFIG,
        'browser': BROWSER_CONFIG,
        'logging': LOGGING_CONFIG,
        'paths': PATH_CONFIG
    }

if __name__ == "__main__":
    # 创建目录
    create_directories()
    # print("目录创建完成")
    
    # 显示配置
    config = get_config()
    # print("\n当前配置:")
    for section, settings in config.items():
        # print(f"\n{section.upper()}:")
        for key, value in settings.items():
            # print(f"  {key}: {value}")
            pass
