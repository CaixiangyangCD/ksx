#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
模拟爬虫爬取的数据，直接写入数据库
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from services.database_manager import get_db_manager
from loguru import logger

# 配置日志
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    level="INFO"
)

async def generate_mock_data():
    """生成模拟爬取数据"""
    mock_data = [
        {
            'ID': 'crawler_001',
            'area': '渝中区',
            'createDateShow': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'MDShow': '华为授权体验店（解放碑店）',
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
            'ID': 'store_002',
            'area': '江北区',
            'createDateShow': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'MDShow': '小米之家（观音桥店）',
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
            'ID': 'store_003',
            'area': '渝中区',
            'createDateShow': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'MDShow': 'OPPO体验店（大坪店）',
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
            'ID': 'store_004',
            'area': '九龙坡区',
            'createDateShow': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'MDShow': 'vivo专卖店（杨家坪店）',
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
            'ID': 'store_005',
            'area': '江北区',
            'createDateShow': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'MDShow': '苹果授权经销商（北城天街店）',
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
        },
        {
            'ID': 'store_006',
            'area': '南岸区',
            'createDateShow': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'MDShow': '三星Galaxy体验店（南坪店）',
            'totalScore': 87.3,
            'monthlyCanceledRate': '3.1%',
            'dailyCanceledRate': '2.2%',
            'monthlyMerchantRefundRate': '1.6%',
            'monthlyOosRefundRate': '0.9%',
            'monthlyJdOosRate': '1.3%',
            'monthlyBadReviews': '6',
            'monthlyBadReviewRate': '0.6%',
            'monthlyPartialRefundRate': '2.0%',
            'dailyMeituanRating': '4.7',
            'dailyElemeRating': '4.6',
            'dailyMeituanReplyRate': '94%',
            'effectReply': '97%',
            'monthlyMeituanPunctualityRate': '95%',
            'monthlyElemeOntimeRate': '93%',
            'monthlyJdFulfillmentRate': '96%',
            'meituanComprehensiveExperienceDivision': '4.5'
        },
        {
            'ID': 'store_007',
            'area': '渝北区',
            'createDateShow': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'MDShow': '荣耀体验店（龙湖天街店）',
            'totalScore': 90.5,
            'monthlyCanceledRate': '2.7%',
            'dailyCanceledRate': '1.8%',
            'monthlyMerchantRefundRate': '1.1%',
            'monthlyOosRefundRate': '0.6%',
            'monthlyJdOosRate': '0.9%',
            'monthlyBadReviews': '3',
            'monthlyBadReviewRate': '0.3%',
            'monthlyPartialRefundRate': '1.7%',
            'dailyMeituanRating': '4.8',
            'dailyElemeRating': '4.8',
            'dailyMeituanReplyRate': '97%',
            'effectReply': '98%',
            'monthlyMeituanPunctualityRate': '98%',
            'monthlyElemeOntimeRate': '96%',
            'monthlyJdFulfillmentRate': '98%',
            'meituanComprehensiveExperienceDivision': '4.8'
        },
        {
            'ID': 'store_008',
            'area': '沙坪坝区',
            'createDateShow': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'MDShow': '一加手机专卖店（三峡广场店）',
            'totalScore': 86.9,
            'monthlyCanceledRate': '3.3%',
            'dailyCanceledRate': '2.4%',
            'monthlyMerchantRefundRate': '1.7%',
            'monthlyOosRefundRate': '0.9%',
            'monthlyJdOosRate': '1.2%',
            'monthlyBadReviews': '5',
            'monthlyBadReviewRate': '0.5%',
            'monthlyPartialRefundRate': '2.2%',
            'dailyMeituanRating': '4.7',
            'dailyElemeRating': '4.6',
            'dailyMeituanReplyRate': '92%',
            'effectReply': '96%',
            'monthlyMeituanPunctualityRate': '93%',
            'monthlyElemeOntimeRate': '91%',
            'monthlyJdFulfillmentRate': '95%',
            'meituanComprehensiveExperienceDivision': '4.4'
        }
    ]
    
    return mock_data

async def deduplicate_data(data: list) -> list:
    """数据去重"""
    try:
        if not data:
            return []
        
        seen_ids = set()
        unique_data = []
        
        for item in data:
            item_id = item.get('ID')
            if item_id and item_id not in seen_ids:
                seen_ids.add(item_id)
                unique_data.append(item)
        
        logger.info(f"数据去重完成: 原始{len(data)}条 -> 去重后{len(unique_data)}条")
        return unique_data
        
    except Exception as e:
        logger.error(f"数据去重失败: {e}")
        return data

async def save_to_database(data: list) -> int:
    """将数据保存到数据库"""
    try:
        if not data:
            logger.warning("没有数据需要保存到数据库")
            return 0
        
        # 获取数据库管理器
        db_manager = get_db_manager()
        
        # 插入数据（会自动去重）
        inserted_count = db_manager.insert_data(data)
        
        logger.info(f"✅ 成功保存 {inserted_count} 条记录到数据库")
        
        # 清理旧数据库（保留近1个月）
        db_manager.cleanup_old_databases(keep_months=1)
        
        return inserted_count
        
    except Exception as e:
        logger.error(f"❌ 保存到数据库失败: {e}")
        return 0

async def init_database():
    """初始化数据库数据"""
    try:
        logger.info("🚀 开始初始化数据库数据...")
        
        # 生成模拟数据
        logger.info("📝 生成模拟爬取数据...")
        mock_data = await generate_mock_data()
        logger.info(f"✅ 生成 {len(mock_data)} 条模拟数据")
        
        # 数据去重
        unique_data = await deduplicate_data(mock_data)
        
        # 保存到数据库
        db_result = await save_to_database(unique_data)
        
        if db_result > 0:
            logger.info(f"🎉 数据库初始化完成！成功保存 {db_result} 条记录")
            
            # 验证数据
            db_manager = get_db_manager()
            result = db_manager.query_data(page=1, page_size=5)
            logger.info(f"📊 验证数据: 数据库中共有 {result['total']} 条记录")
            
            if result['data']:
                logger.info("📄 样例数据:")
                for i, item in enumerate(result['data'][:3]):
                    logger.info(f"   {i+1}. {item.get('MDShow', 'N/A')} - 得分: {item.get('totalScore', 'N/A')}")
            
            return True
        else:
            logger.error("❌ 数据库初始化失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(init_database())
