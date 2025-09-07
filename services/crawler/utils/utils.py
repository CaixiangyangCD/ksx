#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫工具函数模块
"""

import os
import json
import csv
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def ensure_dir(directory: str) -> str:
        """确保目录存在，如果不存在则创建"""
        os.makedirs(directory, exist_ok=True)
        return directory
    
    @staticmethod
    def save_json(data: Any, filepath: str, ensure_ascii: bool = False) -> bool:
        """保存数据为JSON文件"""
        try:
            FileUtils.ensure_dir(os.path.dirname(filepath))
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=ensure_ascii, indent=2)
            return True
        except Exception as e:
            print(f"保存JSON文件失败: {e}")
            return False
    
    @staticmethod
    def load_json(filepath: str) -> Optional[Any]:
        """加载JSON文件"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"加载JSON文件失败: {e}")
            return None
    
    @staticmethod
    def save_csv(data: List[Dict[str, Any]], filepath: str, headers: Optional[List[str]] = None) -> bool:
        """保存数据为CSV文件"""
        try:
            FileUtils.ensure_dir(os.path.dirname(filepath))
            
            if not data:
                return False
            
            if not headers:
                headers = list(data[0].keys())
            
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)
            
            return True
        except Exception as e:
            print(f"保存CSV文件失败: {e}")
            return False
    
    @staticmethod
    def save_text(content: str, filepath: str) -> bool:
        """保存文本内容到文件"""
        try:
            FileUtils.ensure_dir(os.path.dirname(filepath))
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"保存文本文件失败: {e}")
            return False


class TimeUtils:
    """时间工具类"""
    
    @staticmethod
    def get_current_timestamp() -> int:
        """获取当前时间戳"""
        return int(time.time())
    
    @staticmethod
    def get_current_datetime() -> str:
        """获取当前日期时间字符串"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def get_current_date() -> str:
        """获取当前日期字符串"""
        return datetime.now().strftime('%Y-%m-%d')
    
    @staticmethod
    def format_timestamp(timestamp: int, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
        """格式化时间戳"""
        return datetime.fromtimestamp(timestamp).strftime(format_str)
    
    @staticmethod
    def sleep(seconds: float):
        """睡眠指定秒数"""
        time.sleep(seconds)


class DataUtils:
    """数据处理工具类"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """清理文本内容"""
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = ' '.join(text.split())
        # 移除特殊字符
        text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        return text.strip()
    
    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """从文本中提取数字"""
        import re
        numbers = re.findall(r'-?\d+\.?\d*', text)
        return [float(num) for num in numbers]
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """从文本中提取邮箱地址"""
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """从文本中提取URL"""
        import re
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)


class NetworkUtils:
    """网络工具类"""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """检查URL是否有效"""
        import re
        url_pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
        return bool(re.match(url_pattern, url))
    
    @staticmethod
    def get_domain(url: str) -> str:
        """从URL中提取域名"""
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ""
    
    @staticmethod
    def get_path(url: str) -> str:
        """从URL中提取路径"""
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            return parsed.path
        except:
            return ""


class LogUtils:
    """日志工具类"""
    
    @staticmethod
    def log_to_file(message: str, log_file: str = "crawler.log"):
        """记录日志到文件"""
        timestamp = TimeUtils.get_current_datetime()
        log_entry = f"[{timestamp}] {message}\n"
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"写入日志失败: {e}")
    
    @staticmethod
    def log_success(message: str):
        """记录成功日志"""
        print(f"✅ {message}")
        LogUtils.log_to_file(f"SUCCESS: {message}")
    
    @staticmethod
    def log_error(message: str):
        """记录错误日志"""
        print(f"❌ {message}")
        LogUtils.log_to_file(f"ERROR: {message}")
    
    @staticmethod
    def log_info(message: str):
        """记录信息日志"""
        print(f"ℹ️ {message}")
        LogUtils.log_to_file(f"INFO: {message}")
    
    @staticmethod
    def log_warning(message: str):
        """记录警告日志"""
        print(f"⚠️ {message}")
        LogUtils.log_to_file(f"WARNING: {message}")


# 导出所有工具类
__all__ = ['FileUtils', 'TimeUtils', 'DataUtils', 'NetworkUtils', 'LogUtils']
