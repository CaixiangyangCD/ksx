#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟backend环境测试database_manager
"""

import sys
import os

# 模拟从backend目录运行
original_cwd = os.getcwd()
backend_dir = os.path.join(original_cwd, "backend")

print(f"📍 原始目录: {original_cwd}")
print(f"📍 模拟backend目录: {backend_dir}")

# 切换到backend目录
os.chdir(backend_dir)
print(f"📍 当前工作目录: {os.getcwd()}")

# 添加项目根目录到路径
project_root = os.path.dirname(backend_dir)
sys.path.append(project_root)

print(f"📍 项目根目录: {project_root}")

try:
    from services.database_manager import get_db_manager
    
    print("\n🔍 从backend环境测试database_manager...")
    
    db_manager = get_db_manager()
    print(f"📍 数据库路径: {db_manager.base_dir}")
    print(f"📍 路径是否为绝对路径: {db_manager.base_dir.is_absolute()}")
    
    # 检查数据库文件
    db_path = db_manager.get_database_path()
    print(f"📍 今日数据库文件: {db_path}")
    print(f"📍 数据库文件存在: {db_path.exists()}")
    
    if db_path.exists():
        print(f"📍 文件大小: {db_path.stat().st_size} bytes")
        
        # 测试查询
        try:
            result = db_manager.query_data(page=1, page_size=5)
            print(f"✅ 数据库查询成功: {result['total']} 条记录")
            
            if result['data']:
                print("📄 样例数据:")
                for i, item in enumerate(result['data'][:3]):
                    print(f"   {i+1}. {item.get('MDShow', 'N/A')} - 得分: {item.get('totalScore', 'N/A')}")
            
            print("🎉 Backend环境数据库测试成功！")
        except Exception as e:
            print(f"❌ 数据库查询失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ 数据库文件不存在")

finally:
    # 恢复原始目录
    os.chdir(original_cwd)
    print(f"\n📍 恢复到原始目录: {os.getcwd()}")

print("✅ Backend环境测试完成")
