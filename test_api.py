#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API接口测试脚本
"""

import requests
import json

def test_api():
    """测试API接口"""
    base_url = "http://127.0.0.1:8080"
    
    print("🧪 开始测试API接口...")
    
    # 测试健康检查
    print("📝 测试健康检查接口...")
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"✅ 健康检查: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return
    
    # 测试数据查询接口
    print("📝 测试数据查询接口...")
    try:
        response = requests.get(f"{base_url}/api/data")
        result = response.json()
        print(f"✅ 数据查询: {response.status_code}")
        print(f"   总记录数: {result.get('total', 0)}")
        print(f"   返回记录: {len(result.get('data', []))}")
    except Exception as e:
        print(f"❌ 数据查询失败: {e}")
    
    # 测试门店搜索
    print("📝 测试门店搜索接口...")
    try:
        response = requests.get(f"{base_url}/api/data?mdshow=测试")
        result = response.json()
        print(f"✅ 门店搜索: {response.status_code}")
        print(f"   搜索结果: {result.get('total', 0)} 条记录")
    except Exception as e:
        print(f"❌ 门店搜索失败: {e}")
    
    # 测试数据库信息
    print("📝 测试数据库信息接口...")
    try:
        response = requests.get(f"{base_url}/api/database/info")
        result = response.json()
        print(f"✅ 数据库信息: {response.status_code}")
        if result.get('success'):
            info = result.get('data', {})
            print(f"   数据库数量: {info.get('total_databases', 0)}")
            print(f"   总大小: {info.get('total_size_mb', 0)} MB")
    except Exception as e:
        print(f"❌ 数据库信息失败: {e}")
    
    print("🎉 API测试完成！")

if __name__ == "__main__":
    test_api()
