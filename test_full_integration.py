#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的系统集成测试脚本
测试数据库、API服务、前端的完整流程
"""

import requests
import sys
import os
import subprocess
import time
import webbrowser
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from services.database_manager import get_db_manager

def test_database():
    """测试数据库功能"""
    print("🧪 测试数据库功能...")
    
    db_manager = get_db_manager()
    
    # 查询当前数据
    result = db_manager.query_data(page=1, page_size=5)
    print(f"✅ 数据库查询: 总计 {result['total']} 条记录")
    
    if result['data']:
        print("📄 样例数据:")
        for i, item in enumerate(result['data'][:3]):
            print(f"   {i+1}. {item.get('MDShow', 'N/A')} - 得分: {item.get('totalScore', 'N/A')}")
    
    return result['total'] > 0

def test_api_service():
    """测试API服务"""
    print("🧪 测试API服务...")
    
    base_url = "http://127.0.0.1:8080"
    
    try:
        # 健康检查
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API服务健康检查通过")
        else:
            print(f"❌ API健康检查失败: {response.status_code}")
            return False
        
        # 数据查询
        response = requests.get(f"{base_url}/api/data", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API数据查询: 返回 {data.get('total', 0)} 条记录")
            return data.get('total', 0) > 0
        else:
            print(f"❌ API数据查询失败: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务，请确保后端服务正在运行")
        return False
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def test_frontend():
    """测试前端"""
    print("🧪 测试前端...")
    
    # 检查前端构建文件
    dist_path = os.path.join(project_root, "frontend", "dist", "index.html")
    if os.path.exists(dist_path):
        print("✅ 前端构建文件存在")
        
        # 打开测试页面
        test_page = os.path.join(project_root, "test_frontend.html")
        if os.path.exists(test_page):
            print("✅ 前端测试页面准备就绪")
            print(f"📄 测试页面路径: {test_page}")
            return True
        else:
            print("❌ 前端测试页面不存在")
            return False
    else:
        print("❌ 前端构建文件不存在，请先运行 npm run build")
        return False

def check_services_status():
    """检查服务状态"""
    print("🔍 检查服务状态...")
    
    # 检查后端服务
    try:
        response = requests.get("http://127.0.0.1:8080/api/health", timeout=3)
        if response.status_code == 200:
            print("✅ 后端服务正在运行")
            backend_running = True
        else:
            print("❌ 后端服务响应异常")
            backend_running = False
    except:
        print("❌ 后端服务未运行")
        backend_running = False
    
    return backend_running

def start_services_guide():
    """服务启动指南"""
    print("\n📋 服务启动指南:")
    print("1. 启动后端服务:")
    print("   cd backend")
    print("   python main.py")
    print("")
    print("2. 启动前端服务 (可选):")
    print("   cd frontend")
    print("   npm run dev")
    print("")
    print("3. 运行爬虫 (可选):")
    print("   cd services/crawler")
    print("   python main.py")

def main():
    """主测试流程"""
    print("🚀 KSX系统完整集成测试")
    print("=" * 50)
    
    # 测试计数
    tests_passed = 0
    total_tests = 4
    
    # 1. 测试数据库
    if test_database():
        tests_passed += 1
    
    # 2. 检查服务状态
    backend_running = check_services_status()
    if backend_running:
        tests_passed += 1
    
    # 3. 测试API服务
    if backend_running and test_api_service():
        tests_passed += 1
    
    # 4. 测试前端
    if test_frontend():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {tests_passed}/{total_tests} 项测试通过")
    
    if tests_passed == total_tests:
        print("🎉 所有测试通过！系统集成成功！")
        
        # 询问是否打开测试页面
        try:
            choice = input("\n是否打开前端测试页面？(y/n): ").lower().strip()
            if choice in ['y', 'yes', '是', '']:
                test_page = os.path.join(project_root, "test_frontend.html")
                webbrowser.open(f"file://{test_page}")
                print("📄 已打开前端测试页面")
        except KeyboardInterrupt:
            print("\n测试完成")
    else:
        print("❌ 部分测试失败，请检查以下问题:")
        
        if not backend_running:
            print("   - 后端服务未运行")
        
        start_services_guide()
    
    print("\n📝 测试完成！")

if __name__ == "__main__":
    main()
