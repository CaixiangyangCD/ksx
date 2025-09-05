#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理器测试脚本
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from services.database_manager import get_db_manager

def test_database():
    """测试数据库功能"""
    print("🧪 开始测试数据库管理器...")
    
    # 获取数据库管理器
    db_manager = get_db_manager()
    
    # 创建数据库
    print("📝 创建数据库...")
    db_path = db_manager.create_database()
    print(f"✅ 数据库创建成功: {db_path}")
    
    # 测试插入数据
    print("📝 测试插入数据...")
    test_data = [
        {
            'ID': 'test001',
            'MDShow': '测试门店1',
            'area': '1区',
            'totalScore': 85.5,
            'createDateShow': '2024-09-04',
            'monthlyCanceledRate': '5.2%'
        },
        {
            'ID': 'test002', 
            'MDShow': '测试门店2',
            'area': '2区',
            'totalScore': 90.0,
            'createDateShow': '2024-09-04',
            'monthlyCanceledRate': '3.1%'
        }
    ]
    
    inserted = db_manager.insert_data(test_data)
    print(f"✅ 插入记录数: {inserted}")
    
    # 测试查询数据
    print("📝 测试查询数据...")
    result = db_manager.query_data(mdshow_filter="测试", page=1, page_size=10)
    print(f"✅ 查询结果: 找到 {result['total']} 条记录")
    print(f"   数据样例: {result['data'][:2] if result['data'] else '无数据'}")
    
    # 获取数据库信息
    print("📝 获取数据库信息...")
    info = db_manager.get_database_info()
    print(f"✅ 数据库信息: {info['total_databases']} 个数据库, {info['total_size_mb']} MB")
    
    print("🎉 数据库测试完成！")

if __name__ == "__main__":
    test_database()
