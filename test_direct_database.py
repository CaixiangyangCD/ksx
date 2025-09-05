#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试数据库功能，验证数据是否存在
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from services.database_manager import get_db_manager

def test_database_directly():
    """直接测试数据库"""
    print("🧪 直接测试数据库功能...")
    
    # 获取数据库管理器
    db_manager = get_db_manager()
    
    print(f"📍 数据库路径: {db_manager.base_dir}")
    
    # 查询所有数据
    result = db_manager.query_data(page=1, page_size=10)
    print(f"✅ 数据库查询: 总计 {result['total']} 条记录")
    print(f"✅ 当前页记录: {len(result['data'])} 条")
    
    if result['data']:
        print("📄 前5条数据:")
        for i, item in enumerate(result['data'][:5]):
            print(f"   {i+1}. {item.get('MDShow', 'N/A')} - 得分: {item.get('totalScore', 'N/A')} - ID: {item.get('id', 'N/A')}")
    
    # 测试搜索
    search_result = db_manager.query_data(mdshow_filter="华为", page=1, page_size=5)
    print(f"✅ 搜索'华为': 找到 {search_result['total']} 条记录")
    
    # 获取数据库信息
    info = db_manager.get_database_info()
    print(f"✅ 数据库信息: {info['total_databases']} 个数据库, {info['total_size_mb']} MB")
    
    if info['months']:
        print("📂 数据库文件:")
        for month in info['months']:
            print(f"   月份: {month['month']}, 数据库数: {len(month['databases'])}, 大小: {month['size_mb']} MB")
            for db in month['databases']:
                print(f"     - {db['name']} ({db['size_mb']} MB)")

if __name__ == "__main__":
    test_database_directly()
