#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试后端API的数据库路径
"""

import requests
import sys
import os

# 测试后端数据库路径
def test_backend_database_path():
    """测试后端数据库路径"""
    print("🔍 测试后端数据库路径...")
    
    try:
        # 调用数据库信息接口
        response = requests.get("http://127.0.0.1:8080/api/database/info", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ 后端数据库信息接口响应:")
            print(f"   成功状态: {data.get('success', False)}")
            
            if data.get('success') and 'data' in data:
                db_info = data['data']
                print(f"   数据库根目录: {db_info.get('base_dir', 'N/A')}")
                print(f"   数据库总数: {db_info.get('total_databases', 0)}")
                print(f"   总大小: {db_info.get('total_size_mb', 0)} MB")
                
                if db_info.get('months'):
                    print("   月份信息:")
                    for month in db_info['months']:
                        print(f"     {month['month']}: {len(month['databases'])} 个数据库")
                        for db in month['databases']:
                            print(f"       - {db['name']} ({db['size_mb']} MB)")
                else:
                    print("   ❌ 没有找到数据库文件")
            else:
                print("   ❌ 数据库信息获取失败")
        else:
            print(f"❌ 后端数据库信息接口失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试后端数据库路径失败: {e}")

def test_backend_data_query():
    """测试后端数据查询"""
    print("\n🔍 测试后端数据查询...")
    
    try:
        # 调用数据查询接口
        response = requests.get("http://127.0.0.1:8080/api/data?page=1&page_size=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ 后端数据查询接口响应:")
            print(f"   成功状态: {data.get('success', False)}")
            print(f"   总记录数: {data.get('total', 0)}")
            print(f"   返回记录数: {len(data.get('data', []))}")
            print(f"   当前页: {data.get('page', 0)}")
            print(f"   每页大小: {data.get('page_size', 0)}")
            print(f"   总页数: {data.get('total_pages', 0)}")
            
            if data.get('data'):
                print("   样例数据:")
                for i, item in enumerate(data['data'][:3]):
                    print(f"     {i+1}. {item.get('MDShow', 'N/A')} - 得分: {item.get('totalScore', 'N/A')}")
            else:
                print("   ❌ 没有返回数据")
        else:
            print(f"❌ 后端数据查询接口失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试后端数据查询失败: {e}")

def compare_with_direct_database():
    """与直接数据库查询对比"""
    print("\n🔍 与直接数据库查询对比...")
    
    try:
        # 添加项目根目录到路径
        project_root = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(project_root)
        
        from services.database_manager import get_db_manager
        
        db_manager = get_db_manager()
        print(f"✅ 直接数据库查询:")
        print(f"   数据库路径: {db_manager.base_dir}")
        
        result = db_manager.query_data(page=1, page_size=5)
        print(f"   总记录数: {result['total']}")
        print(f"   返回记录数: {len(result['data'])}")
        
        if result['data']:
            print("   样例数据:")
            for i, item in enumerate(result['data'][:3]):
                print(f"     {i+1}. {item.get('MDShow', 'N/A')} - 得分: {item.get('totalScore', 'N/A')}")
                
    except Exception as e:
        print(f"❌ 直接数据库查询失败: {e}")

if __name__ == "__main__":
    test_backend_database_path()
    test_backend_data_query()
    compare_with_direct_database()
