#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试数据库路径问题
检查不同服务使用的数据库路径是否一致
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def test_database_paths():
    """测试不同位置调用时的数据库路径"""
    print("🔍 检查数据库路径问题...")
    
    # 1. 从项目根目录调用
    print(f"📍 当前工作目录: {os.getcwd()}")
    print(f"📍 项目根目录: {project_root}")
    
    from services.database_manager import get_db_manager
    db_manager = get_db_manager()
    print(f"📍 数据库管理器路径: {db_manager.base_dir}")
    
    # 2. 检查数据库文件是否存在
    db_path = db_manager.get_database_path()
    print(f"📍 今日数据库路径: {db_path}")
    print(f"📍 数据库文件存在: {db_path.exists()}")
    
    if db_path.exists():
        print(f"📍 文件大小: {db_path.stat().st_size} bytes")
    
    # 3. 测试查询
    try:
        result = db_manager.query_data(page=1, page_size=5)
        print(f"✅ 数据库查询成功: {result['total']} 条记录")
    except Exception as e:
        print(f"❌ 数据库查询失败: {e}")
    
    print(f"\n📍 当前目录: {os.getcwd()}")

def test_crawler_database_save():
    """测试爬虫数据库保存功能"""
    print("\n🧪 测试爬虫数据库保存功能...")
    
    # 模拟爬虫数据
    test_data = [
        {
            'ID': 'debug_test_001',
            'area': '测试区',
            'createDateShow': '2024-09-04',
            'MDShow': '测试门店（调试用）',
            'totalScore': 99.9,
            'monthlyCanceledRate': '1.0%',
            'dailyCanceledRate': '0.5%'
        }
    ]
    
    try:
        from services.database_manager import get_db_manager
        db_manager = get_db_manager()
        print(f"📍 使用数据库路径: {db_manager.base_dir}")
        
        # 插入测试数据
        inserted_count = db_manager.insert_data(test_data)
        print(f"✅ 成功插入 {inserted_count} 条测试记录")
        
        # 验证数据
        result = db_manager.query_data(mdshow_filter="测试门店", page=1, page_size=5)
        print(f"✅ 验证查询: 找到 {result['total']} 条测试记录")
        
        return True
        
    except Exception as e:
        print(f"❌ 爬虫数据库保存测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_database_paths()
    test_crawler_database_save()
