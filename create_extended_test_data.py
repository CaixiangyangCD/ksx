#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建扩展的测试数据集，包含更多记录
"""

import sys
import os
import random
from datetime import datetime, timedelta

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

def generate_random_data(base_id: int, store_names: list) -> dict:
    """生成随机测试数据"""
    return {
        "ID": str(50000 + base_id),
        "area": random.choice(["1区", "2区", "3区", "4区", "5区"]),
        "createDateShow": "2024-09-04",
        "MDShow": random.choice(store_names),
        "totalScore": round(random.uniform(75.0, 98.0), 2),
        "monthlyCanceledRate": f"{random.uniform(1.0, 5.0):.2f}%",
        "dailyCanceledRate": f"{random.uniform(1.0, 5.0):.2f}%",
        "monthlyMerchantRefundRate": f"{random.uniform(0.0, 1.0):.2f}%",
        "monthlyOosRefundRate": f"{random.uniform(0.0, 0.5):.2f}%",
        "monthlyJdOosRate": f"{random.uniform(0.0, 0.3):.2f}%",
        "monthlyBadReviews": str(random.randint(0, 10)),
        "monthlyBadReviewRate": f"{random.uniform(0.0, 2.0):.2f}%",
        "monthlyPartialRefundRate": f"{random.uniform(0.0, 1.0):.2f}%",
        "dailyMeituanRating": f"{random.uniform(4.0, 5.0):.1f}",
        "dailyElemeRating": f"{random.uniform(4.0, 5.0):.1f}",
        "dailyMeituanReplyRate": f"{random.uniform(80.0, 99.0):.2f}%",
        "effectReply": random.choice(["正常", "异常"]),
        "monthlyMeituanPunctualityRate": f"{random.uniform(85.0, 99.0):.2f}%",
        "monthlyElemeOntimeRate": f"{random.uniform(85.0, 99.0):.2f}%",
        "monthlyJdFulfillmentRate": f"{random.uniform(80.0, 95.0):.2f}%",
        "meituanComprehensiveExperienceDivision": f"{random.uniform(90.0, 99.0):.1f}",
        "monthlyAvgStockRate": f"{random.uniform(90.0, 99.0):.2f}%",
        "monthlyAvgTop500StockRate": f"{random.uniform(88.0, 98.0):.2f}%",
        "monthlyAvgDirectStockRate": f"{random.uniform(75.0, 95.0):.2f}%",
        "dailyTop500StockRate": f"{random.uniform(88.0, 98.0):.2f}%",
        "dailyWarehouseSoldOut": str(random.randint(50, 300)),
        "dailyWarehouseStockRate": f"{random.uniform(92.0, 99.0):.2f}%",
        "dailyDirectSoldOut": str(random.randint(5, 50)),
        "dailyDirectStockRate": f"{random.uniform(70.0, 90.0):.2f}%",
        "dailyHybridSoldOut": str(random.randint(1, 20)),
        "dailyStockAvailability": f"{random.uniform(90.0, 99.0):.2f}%",
        "dailyHybridStockRate": f"{random.uniform(85.0, 97.0):.2f}%",
        "stockNoLocation": str(random.randint(0, 10)),
        "expiryManagement": random.choice(["正常", "异常"]),
        "inventoryLockOrders": str(random.randint(0, 5)),
        "trainingCompleted": random.choice(["正常", "异常"]),
        "monthlyManhourPer100Orders": round(random.uniform(5.0, 12.0), 2),
        "monthlyTotalLoss": round(random.uniform(-500.0, 100.0), 2),
        "monthlyTotalLossRate": f"{random.uniform(-3.0, 1.0):.2f}%",
        "monthlyAvgDeliveryFee": round(random.uniform(4.0, 8.0), 2),
        "dailyAvgDeliveryFee": round(random.uniform(4.0, 8.0), 2),
        "monthlyCumulativeCancelRateScore": f"{random.uniform(70.0, 100.0):.2f}",
        "monthlyMerchantLiabilityRefundRateScore": f"{random.uniform(80.0, 100.0):.2f}",
        "monthlyStockoutRefundRateScore": f"{random.uniform(85.0, 100.0):.2f}",
        "monthlyNegativeReviewRateScore": f"{random.uniform(80.0, 100.0):.2f}",
        "monthlyPartialRefundRateScore": f"{random.uniform(85.0, 100.0):.2f}",
        "dailyMeituanRatingScore": f"{random.uniform(60.0, 100.0):.0f}",
        "dailyElemeRatingScore": f"{random.uniform(60.0, 100.0):.0f}",
        "monthlyMeituanDeliveryPunctualityRateScore": f"{random.uniform(85.0, 100.0):.0f}",
        "monthlyElemeTimelyDeliveryRateScore": f"{random.uniform(85.0, 100.0):.0f}",
        "validReplyWeightingPenalty": "0",
        "monthlyAverageStockRateWeightingPenalty": "0",
        "monthlyAverageTop500StockRateWeightingPenalty": "0",
        "monthlyAverageDirectStockRateWeightingPenalty": "0",
        "newProductComplianceListingWeightingPenalty": "0",
        "expiryManagementWeightingPenalty": "0",
        "inventoryLockWeightingPenalty": "0",
        "monthlyCumulativeHundredOrdersManhourWeightingPenalty": "0",
        "totalScoreWithoutWeightingPenalty": f"{random.uniform(75.0, 98.0):.2f}",
        "monthlyCumulativeMerchantLiabilityRefundRateWeightingPenalty": "0",
        "monthlyCumulativeOutOfStockRefundRateWeightingPenalty": "0",
        "meituanComplexExperienceScoreWeightingPenalty": "0",
        "meituanRatingWeightingPenalty": "0",
        "elemeRatingWeightingPenalty": "0",
        "partialRefundWeightingPenalty": "0",
        "trainingCompletedWeightingPenalty": "0",
        "totalWeightingPenalty": "0"
    }

def create_extended_test_data():
    """创建扩展的测试数据"""
    logger.info("🏗️ 开始创建扩展测试数据...")
    
    # 门店名称列表
    store_names = [
        "苹果授权经销商（渝中店）",
        "华为体验店（江北店）",
        "小米之家（南岸店）",
        "OPPO专卖店（九龙坡店）",
        "vivo体验店（渝北店）",
        "三星Galaxy店（沙坪坝店）",
        "一加手机店（大渡口店）",
        "魅族专卖店（北碚店）",
        "荣耀体验店（巴南店）",
        "realme专卖店（綦江店）",
        "京东便利店（万州店）",
        "天猫小店（涪陵店）",
        "苏宁易购（黔江店）",
        "国美电器（长寿店）",
        "永辉超市（江津店）"
    ]
    
    # 生成15条扩展数据
    extended_data = []
    for i in range(15):
        extended_data.append(generate_random_data(i, store_names))
    
    try:
        # 获取数据库管理器
        db_manager = get_db_manager()
        
        # 插入数据
        inserted_count = db_manager.insert_data(extended_data)
        logger.info(f"✅ 成功插入 {inserted_count} 条扩展数据")
        
        # 验证总数据
        result = db_manager.query_data(page=1, page_size=10)
        logger.info(f"📊 数据库总记录数: {result['total']} 条")
        
        if result['data']:
            logger.info("📄 最新数据样例:")
            for i, item in enumerate(result['data'][:5]):
                logger.info(f"   {i+1}. ID={item.get('id', 'N/A')}, 门店={item.get('MDShow', 'N/A')}, 得分={item.get('totalScore', 'N/A')}")
        
        logger.info("🎉 扩展测试数据创建成功！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 创建扩展测试数据失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    create_extended_test_data()
