#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置数据库管理模块
管理门店配置和导出规则
"""

import sqlite3
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
# 尝试导入loguru，如果失败则使用标准logging
try:
    from loguru import logger
    LOGGER_AVAILABLE = True
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    LOGGER_AVAILABLE = False
    print("警告: loguru不可用，使用标准logging模块")

def get_config_db_path():
    """获取配置数据库路径，支持打包后的应用"""
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的情况
        # 在macOS中，应用的实际路径是.app/Contents/MacOS/
        # 我们需要找到.app的根目录
        from pathlib import Path
        executable_path = Path(sys.executable)
        if executable_path.name.endswith('.app'):
            # 如果executable本身就是.app
            app_dir = executable_path
        else:
            # 如果executable在.app/Contents/MacOS/中
            app_dir = executable_path.parent.parent.parent
        
        config_db_path = app_dir / "database" / "config.db"
        return str(config_db_path)
    else:
        # 开发环境
        current_file = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_file)
        return os.path.join(project_root, "database", "config.db")

class ConfigDatabaseManager:
    """配置数据库管理器"""
    
    def __init__(self, db_path: str = None):
        """
        初始化配置数据库管理器
        
        Args:
            db_path: 数据库文件路径，默认为backend/config.db
        """
        if db_path is None:
            # 使用正确的配置数据库路径
            self.db_path = get_config_db_path()
        else:
            self.db_path = db_path
        
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建门店表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        store_name TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建导出规则表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS export_rules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        rule_name TEXT NOT NULL,
                        selected_stores TEXT NOT NULL,  -- JSON格式存储选中的门店ID列表
                        is_default BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建字段导出规则表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS export_field_rules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        rule_name TEXT NOT NULL,
                        selected_fields TEXT NOT NULL,  -- JSON格式存储选中的字段列表
                        is_default BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("配置数据库初始化完成")
                
        except Exception as e:
            logger.error(f"配置数据库初始化失败: {e}")
            raise
    
    def add_store(self, store_name: str) -> bool:
        """
        添加门店
        
        Args:
            store_name: 门店名称
            
        Returns:
            bool: 是否成功添加
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO stores (store_name) 
                    VALUES (?)
                """, (store_name,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"新增门店: {store_name}")
                    return True
                else:
                    logger.info(f"门店已存在: {store_name}")
                    return False
                    
        except Exception as e:
            logger.error(f"添加门店失败: {e}")
            return False
    
    def get_all_stores(self) -> List[Dict[str, Any]]:
        """
        获取所有门店
        
        Returns:
            List[Dict]: 门店列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, store_name, created_at, updated_at 
                    FROM stores 
                    ORDER BY store_name
                """)
                
                stores = []
                for row in cursor.fetchall():
                    stores.append({
                        'id': row[0],
                        'store_name': row[1],
                        'created_at': row[2],
                        'updated_at': row[3]
                    })
                
                return stores
                
        except Exception as e:
            logger.error(f"获取门店列表失败: {e}")
            return []
    
    def save_export_rule(self, selected_stores: List[str]) -> bool:
        """
        保存导出规则（只保存一条规则）
        
        Args:
            selected_stores: 选中的门店名称列表
            
        Returns:
            bool: 是否成功保存
        """
        try:
            import json
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 清空所有现有规则
                cursor.execute("DELETE FROM export_rules")
                
                # 插入新规则
                cursor.execute("""
                    INSERT INTO export_rules (rule_name, selected_stores, is_default)
                    VALUES (?, ?, ?)
                """, ("默认导出规则", json.dumps(selected_stores), True))
                
                conn.commit()
                logger.info(f"保存导出规则，选中门店: {len(selected_stores)}个")
                return True
                
        except Exception as e:
            logger.error(f"保存导出规则失败: {e}")
            return False
    
    def get_export_rule(self) -> Optional[Dict[str, Any]]:
        """
        获取导出规则（只返回一条规则）
        
        Returns:
            Dict: 导出规则，如果没有则返回None
        """
        try:
            import json
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, rule_name, selected_stores, is_default, created_at, updated_at
                    FROM export_rules 
                    LIMIT 1
                """)
                
                row = cursor.fetchone()
                if row:
                    try:
                        selected_stores = json.loads(row[2])
                    except:
                        selected_stores = []
                    
                    return {
                        'id': row[0],
                        'rule_name': row[1],
                        'selected_stores': selected_stores,
                        'is_default': bool(row[3]),
                        'created_at': row[4],
                        'updated_at': row[5]
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"获取导出规则失败: {e}")
            return None
    
    def get_default_rule(self) -> Optional[Dict[str, Any]]:
        """
        获取默认导出规则
        
        Returns:
            Dict: 默认规则，如果没有则返回None
        """
        rules = self.get_export_rules()
        for rule in rules:
            if rule['is_default']:
                return rule
        return None
    
    def delete_rule(self, rule_id: int) -> bool:
        """
        删除导出规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            bool: 是否成功删除
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM export_rules WHERE id = ?", (rule_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"删除导出规则: {rule_id}")
                    return True
                else:
                    logger.warning(f"导出规则不存在: {rule_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"删除导出规则失败: {e}")
            return False
    
    def save_export_field_rule(self, selected_fields: List[str]) -> bool:
        """
        保存字段导出规则（只保存一个规则）
        
        Args:
            selected_fields: 选中的字段列表
            
        Returns:
            bool: 是否成功保存
        """
        try:
            import json
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 删除所有现有规则
                cursor.execute("DELETE FROM export_field_rules")
                
                # 插入新规则
                cursor.execute("""
                    INSERT INTO export_field_rules (rule_name, selected_fields, is_default)
                    VALUES (?, ?, ?)
                """, ("默认字段规则", json.dumps(selected_fields), True))
                
                conn.commit()
                logger.info(f"保存字段导出规则: {len(selected_fields)} 个字段")
                return True
                
        except Exception as e:
            logger.error(f"保存字段导出规则失败: {e}")
            return False
    
    def get_export_field_rule(self) -> Optional[Dict[str, Any]]:
        """
        获取字段导出规则
        
        Returns:
            Optional[Dict[str, Any]]: 字段导出规则或None
        """
        try:
            import json
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, rule_name, selected_fields, is_default, created_at, updated_at
                    FROM export_field_rules
                    ORDER BY updated_at DESC
                    LIMIT 1
                """)
                
                result = cursor.fetchone()
                if result:
                    try:
                        selected_fields = json.loads(result[2])
                    except:
                        selected_fields = []
                    
                    return {
                        "id": result[0],
                        "rule_name": result[1],
                        "selected_fields": selected_fields,
                        "is_default": bool(result[3]),
                        "created_at": result[4],
                        "updated_at": result[5]
                    }
                return None
                
        except Exception as e:
            logger.error(f"获取字段导出规则失败: {e}")
            return None
    
    def get_export_fields(self) -> List[Dict[str, Any]]:
        """
        获取所有可导出的字段列表
        
        Returns:
            List[Dict]: 字段列表
        """
        try:
            # 从数据库管理器获取字段定义
            from services.database_manager import get_db_manager
            db_manager = get_db_manager()
            
            # 获取schema中的字段定义
            fields = []
            for field in db_manager.schema:
                fields.append({
                    "name": field["name"],
                    "label": field["label"],
                    "type": field["type"]
                })
            
            return fields
            
        except Exception as e:
            logger.error(f"获取导出字段失败: {e}")
            return []

# 全局配置数据库管理器实例
config_db_manager = ConfigDatabaseManager()
