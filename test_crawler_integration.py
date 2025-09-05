#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫集成测试脚本
仅测试数据库保存功能，不进行实际爬取
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from services.database_manager import get_db_manager

async def test_crawler_database():
    """测试爬虫数据库集成"""
    print("🧪 开始测试爬虫数据库集成...")
    
    # 模拟爬取到的数据
    mock_crawled_data = [
        {
            'ID': 'ksx001',
            'area': '1区',
            'createDateShow': '2024-09-04',
            'MDShow': '华为授权体验店（龙湖天街店）',
            'totalScore': 88.5,
            'monthlyCanceledRate': '3.2%',
            'dailyCanceledRate': '2.1%',
            'monthlyMerchantRefundRate': '1.5%',
            'monthlyOosRefundRate': '0.8%',
            'monthlyJdOosRate': '1.2%',
            'monthlyBadReviews': '5',
            'monthlyBadReviewRate': '0.5%',
            'monthlyPartialRefundRate': '2.1%',
            'dailyMeituanRating': '4.8',
            'dailyElemeRating': '4.7',
            'dailyMeituanReplyRate': '95%',
            'effectReply': '98%',
            'monthlyMeituanPunctualityRate': '96%',
            'monthlyElemeOntimeRate': '94%',
            'monthlyJdFulfillmentRate': '97%',
            'meituanComprehensiveExperienceDivision': '4.6'
        },
        {
            'ID': 'ksx002',
            'area': '2区',
            'createDateShow': '2024-09-04',
            'MDShow': '小米之家（万象城店）',
            'totalScore': 92.3,
            'monthlyCanceledRate': '2.8%',
            'dailyCanceledRate': '1.9%',
            'monthlyMerchantRefundRate': '1.2%',
            'monthlyOosRefundRate': '0.6%',
            'monthlyJdOosRate': '0.9%',
            'monthlyBadReviews': '2',
            'monthlyBadReviewRate': '0.2%',
            'monthlyPartialRefundRate': '1.8%',
            'dailyMeituanRating': '4.9',
            'dailyElemeRating': '4.8',
            'dailyMeituanReplyRate': '97%',
            'effectReply': '99%',
            'monthlyMeituanPunctualityRate': '98%',
            'monthlyElemeOntimeRate': '96%',
            'monthlyJdFulfillmentRate': '98%',
            'meituanComprehensiveExperienceDivision': '4.8'
        },
        {
            'ID': 'ksx003',
            'area': '1区',
            'createDateShow': '2024-09-04',
            'MDShow': 'OPPO体验店（解放碑店）',
            'totalScore': 85.7,
            'monthlyCanceledRate': '3.5%',
            'dailyCanceledRate': '2.3%',
            'monthlyMerchantRefundRate': '1.8%',
            'monthlyOosRefundRate': '1.0%',
            'monthlyJdOosRate': '1.4%',
            'monthlyBadReviews': '7',
            'monthlyBadReviewRate': '0.7%',
            'monthlyPartialRefundRate': '2.3%',
            'dailyMeituanRating': '4.7',
            'dailyElemeRating': '4.6',
            'dailyMeituanReplyRate': '93%',
            'effectReply': '96%',
            'monthlyMeituanPunctualityRate': '94%',
            'monthlyElemeOntimeRate': '92%',
            'monthlyJdFulfillmentRate': '95%',
            'meituanComprehensiveExperienceDivision': '4.5'
        }
    ]
    
    print("📝 测试数据库保存功能...")
    
    # 获取数据库管理器
    db_manager = get_db_manager()
    
    # 保存数据
    inserted_count = db_manager.insert_data(mock_crawled_data)
    print(f"✅ 成功保存 {inserted_count} 条记录到数据库")
    
    # 测试查询功能
    print("📝 测试数据查询功能...")
    result = db_manager.query_data(page=1, page_size=10)
    print(f"✅ 查询结果: 总计 {result['total']} 条记录")
    
    # 测试门店搜索
    print("📝 测试门店搜索功能...")
    search_result = db_manager.query_data(mdshow_filter="华为", page=1, page_size=10)
    print(f"✅ 搜索结果: 找到 {search_result['total']} 条华为相关记录")
    
    # 测试去重功能
    print("📝 测试数据去重功能...")
    duplicate_data = [mock_crawled_data[0]]  # 重复第一条数据
    inserted_duplicate = db_manager.insert_data(duplicate_data)
    print(f"✅ 重复数据插入: {inserted_duplicate} 条（应该为0，因为已去重）")
    
    # 获取数据库信息
    print("📝 获取数据库信息...")
    info = db_manager.get_database_info()
    print(f"✅ 数据库信息: {info['total_databases']} 个数据库, {info['total_size_mb']} MB")
    
    print("🎉 爬虫数据库集成测试完成！")

if __name__ == "__main__":
    asyncio.run(test_crawler_database())
