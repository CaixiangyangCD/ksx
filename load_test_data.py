#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加载测试数据到数据库的脚本
确保API能够读取到数据
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from services.database_manager import get_db_manager

def load_test_data():
    """加载测试数据到数据库"""
    print("📥 开始加载测试数据...")
    
    # 模拟爬取到的数据（更多样例）
    test_data = [
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
        },
        {
            'ID': 'ksx004',
            'area': '3区',
            'createDateShow': '2024-09-04',
            'MDShow': 'vivo专卖店（中央公园店）',
            'totalScore': 89.2,
            'monthlyCanceledRate': '2.9%',
            'dailyCanceledRate': '2.0%',
            'monthlyMerchantRefundRate': '1.3%',
            'monthlyOosRefundRate': '0.7%',
            'monthlyJdOosRate': '1.0%',
            'monthlyBadReviews': '4',
            'monthlyBadReviewRate': '0.4%',
            'monthlyPartialRefundRate': '1.9%',
            'dailyMeituanRating': '4.8',
            'dailyElemeRating': '4.7',
            'dailyMeituanReplyRate': '96%',
            'effectReply': '98%',
            'monthlyMeituanPunctualityRate': '97%',
            'monthlyElemeOntimeRate': '95%',
            'monthlyJdFulfillmentRate': '97%',
            'meituanComprehensiveExperienceDivision': '4.7'
        },
        {
            'ID': 'ksx005',
            'area': '2区',
            'createDateShow': '2024-09-04',
            'MDShow': '苹果授权经销商（观音桥店）',
            'totalScore': 94.1,
            'monthlyCanceledRate': '2.5%',
            'dailyCanceledRate': '1.7%',
            'monthlyMerchantRefundRate': '1.0%',
            'monthlyOosRefundRate': '0.5%',
            'monthlyJdOosRate': '0.8%',
            'monthlyBadReviews': '1',
            'monthlyBadReviewRate': '0.1%',
            'monthlyPartialRefundRate': '1.5%',
            'dailyMeituanRating': '4.9',
            'dailyElemeRating': '4.9',
            'dailyMeituanReplyRate': '98%',
            'effectReply': '99%',
            'monthlyMeituanPunctualityRate': '99%',
            'monthlyElemeOntimeRate': '97%',
            'monthlyJdFulfillmentRate': '99%',
            'meituanComprehensiveExperienceDivision': '4.9'
        }
    ]
    
    # 获取数据库管理器
    db_manager = get_db_manager()
    
    print(f"📍 数据库路径: {db_manager.base_dir}")
    
    # 保存数据
    inserted_count = db_manager.insert_data(test_data)
    print(f"✅ 成功加载 {inserted_count} 条测试数据")
    
    # 验证数据
    result = db_manager.query_data(page=1, page_size=10)
    print(f"✅ 验证数据: 总计 {result['total']} 条记录")
    
    # 显示样例数据
    if result['data']:
        print("📄 样例数据:")
        for i, item in enumerate(result['data'][:3]):
            print(f"   {i+1}. {item.get('MDShow', 'N/A')} - 得分: {item.get('totalScore', 'N/A')}")
    
    print("🎉 测试数据加载完成！")

if __name__ == "__main__":
    load_test_data()
