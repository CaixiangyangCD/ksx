#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试爬虫数据库保存功能
模拟爬虫的save_to_database方法
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
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

async def save_to_database(data: list) -> int:
    """将数据保存到数据库（模拟爬虫的方法）"""
    try:
        if not data:
            logger.warning("没有数据需要保存到数据库")
            return 0
        
        logger.info(f"开始保存 {len(data)} 条数据到数据库...")
        
        # 获取数据库管理器
        db_manager = get_db_manager()
        logger.info(f"数据库路径: {db_manager.base_dir}")
        
        # 插入数据（会自动去重）
        inserted_count = db_manager.insert_data(data)
        
        logger.info(f"✅ 成功保存 {inserted_count} 条记录到数据库")
        
        # 清理旧数据库（保留近1个月）
        db_manager.cleanup_old_databases(keep_months=1)
        
        return inserted_count
        
    except Exception as e:
        logger.error(f"❌ 保存到数据库失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        return 0

async def test_crawler_save():
    """测试爬虫保存功能"""
    logger.info("🧪 开始测试爬虫数据库保存功能...")
    
    # 模拟爬取到的数据
    test_data = [
        {
            'ID': 'crawler_test_001',
            'area': '渝中区',
            'createDateShow': datetime.now().strftime('%Y-%m-%d'),
            'MDShow': '爬虫测试门店001',
            'totalScore': 88.8,
            'monthlyCanceledRate': '2.5%',
            'dailyCanceledRate': '1.8%',
            'monthlyMerchantRefundRate': '1.2%',
            'monthlyOosRefundRate': '0.6%',
            'monthlyJdOosRate': '0.9%',
            'monthlyBadReviews': '3',
            'monthlyBadReviewRate': '0.3%',
            'monthlyPartialRefundRate': '1.7%',
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
            'ID': 'crawler_test_002',
            'area': '江北区',
            'createDateShow': datetime.now().strftime('%Y-%m-%d'),
            'MDShow': '爬虫测试门店002',
            'totalScore': 91.2,
            'monthlyCanceledRate': '2.1%',
            'dailyCanceledRate': '1.5%',
            'monthlyMerchantRefundRate': '1.0%',
            'monthlyOosRefundRate': '0.4%',
            'monthlyJdOosRate': '0.7%',
            'monthlyBadReviews': '2',
            'monthlyBadReviewRate': '0.2%',
            'monthlyPartialRefundRate': '1.5%',
            'dailyMeituanRating': '4.9',
            'dailyElemeRating': '4.8',
            'dailyMeituanReplyRate': '98%',
            'effectReply': '99%',
            'monthlyMeituanPunctualityRate': '98%',
            'monthlyElemeOntimeRate': '96%',
            'monthlyJdFulfillmentRate': '98%',
            'meituanComprehensiveExperienceDivision': '4.8'
        }
    ]
    
    # 保存数据
    result = await save_to_database(test_data)
    
    if result > 0:
        logger.info(f"🎉 爬虫数据库保存测试成功！保存了 {result} 条记录")
        
        # 验证数据
        db_manager = get_db_manager()
        query_result = db_manager.query_data(mdshow_filter="爬虫测试", page=1, page_size=10)
        logger.info(f"📊 验证查询: 找到 {query_result['total']} 条爬虫测试记录")
        
        return True
    else:
        logger.error("❌ 爬虫数据库保存测试失败")
        return False

if __name__ == "__main__":
    asyncio.run(test_crawler_save())
