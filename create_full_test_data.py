#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建包含完整字段的测试数据
基于data.json的真实数据结构
"""

import sys
import os
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

def create_complete_test_data():
    """创建包含完整字段的测试数据"""
    logger.info("🏗️ 开始创建完整字段的测试数据...")
    
    # 基于data.json中的真实数据结构创建测试数据
    test_data = [
        {
            "ID": "44837",
            "area": "1区",
            "createDateShow": "2024-09-04",
            "MDShow": "京东便利店（城东店）",
            "totalScore": 92.28,
            "monthlyCanceledRate": "3.01%",
            "dailyCanceledRate": "3.01%",
            "monthlyMerchantRefundRate": "0.16%",
            "monthlyOosRefundRate": "0.00%",
            "monthlyJdOosRate": "0.00%",
            "monthlyBadReviews": "0",
            "monthlyBadReviewRate": "0.00%",
            "monthlyPartialRefundRate": "0.20%",
            "dailyMeituanRating": "4.6",
            "dailyElemeRating": "4.9",
            "dailyMeituanReplyRate": "85.26%",
            "effectReply": "正常",
            "monthlyMeituanPunctualityRate": "94.24%",
            "monthlyElemeOntimeRate": "92.55%",
            "monthlyJdFulfillmentRate": "87.50%",
            "meituanComprehensiveExperienceDivision": "94.8",
            "monthlyAvgStockRate": "97.46%",
            "monthlyAvgTop500StockRate": "95.20%",
            "monthlyAvgDirectStockRate": "82.99%",
            "dailyTop500StockRate": "95.20%",
            "dailyWarehouseSoldOut": "189",
            "dailyWarehouseStockRate": "97.71%",
            "dailyDirectSoldOut": "20",
            "dailyDirectStockRate": "77.27%",
            "dailyHybridSoldOut": "5",
            "dailyStockAvailability": "97.46%",
            "dailyHybridStockRate": "91.53%",
            "stockNoLocation": "3",
            "expiryManagement": "正常",
            "inventoryLockOrders": "0",
            "trainingCompleted": "正常",
            "monthlyManhourPer100Orders": 8.53,
            "monthlyTotalLoss": -362.49,
            "monthlyTotalLossRate": "-1.86%",
            "monthlyAvgDeliveryFee": 5.73,
            "dailyAvgDeliveryFee": 5.73,
            "monthlyCumulativeCancelRateScore": "86.57",
            "monthlyMerchantLiabilityRefundRateScore": "89.66",
            "monthlyStockoutRefundRateScore": "100",
            "monthlyNegativeReviewRateScore": "100",
            "monthlyPartialRefundRateScore": "92.01",
            "dailyMeituanRatingScore": "60",
            "dailyElemeRatingScore": "86.67",
            "monthlyMeituanDeliveryPunctualityRateScore": "100",
            "monthlyElemeTimelyDeliveryRateScore": "100",
            "validReplyWeightingPenalty": "0",
            "monthlyAverageStockRateWeightingPenalty": "0",
            "monthlyAverageTop500StockRateWeightingPenalty": "0",
            "monthlyAverageDirectStockRateWeightingPenalty": "0",
            "newProductComplianceListingWeightingPenalty": "0",
            "expiryManagementWeightingPenalty": "0",
            "inventoryLockWeightingPenalty": "0",
            "monthlyCumulativeHundredOrdersManhourWeightingPenalty": "0",
            "totalScoreWithoutWeightingPenalty": "92.28",
            "monthlyCumulativeMerchantLiabilityRefundRateWeightingPenalty": "0",
            "monthlyCumulativeOutOfStockRefundRateWeightingPenalty": "0",
            "meituanComplexExperienceScoreWeightingPenalty": "0",
            "meituanRatingWeightingPenalty": "0",
            "elemeRatingWeightingPenalty": "0",
            "partialRefundWeightingPenalty": "0",
            "trainingCompletedWeightingPenalty": "0",
            "totalWeightingPenalty": "0"
        },
        {
            "ID": "44838",
            "area": "2区",
            "createDateShow": "2024-09-04",
            "MDShow": "华为授权体验店（观音桥店）",
            "totalScore": 88.45,
            "monthlyCanceledRate": "2.85%",
            "dailyCanceledRate": "2.85%",
            "monthlyMerchantRefundRate": "0.22%",
            "monthlyOosRefundRate": "0.05%",
            "monthlyJdOosRate": "0.00%",
            "monthlyBadReviews": "2",
            "monthlyBadReviewRate": "0.15%",
            "monthlyPartialRefundRate": "0.18%",
            "dailyMeituanRating": "4.7",
            "dailyElemeRating": "4.8",
            "dailyMeituanReplyRate": "88.35%",
            "effectReply": "正常",
            "monthlyMeituanPunctualityRate": "95.12%",
            "monthlyElemeOntimeRate": "93.24%",
            "monthlyJdFulfillmentRate": "89.75%",
            "meituanComprehensiveExperienceDivision": "95.2",
            "monthlyAvgStockRate": "96.85%",
            "monthlyAvgTop500StockRate": "94.68%",
            "monthlyAvgDirectStockRate": "85.42%",
            "dailyTop500StockRate": "94.68%",
            "dailyWarehouseSoldOut": "156",
            "dailyWarehouseStockRate": "98.12%",
            "dailyDirectSoldOut": "18",
            "dailyDirectStockRate": "79.86%",
            "dailyHybridSoldOut": "4",
            "dailyStockAvailability": "96.85%",
            "dailyHybridStockRate": "93.24%",
            "stockNoLocation": "2",
            "expiryManagement": "正常",
            "inventoryLockOrders": "0",
            "trainingCompleted": "正常",
            "monthlyManhourPer100Orders": 7.92,
            "monthlyTotalLoss": -245.18,
            "monthlyTotalLossRate": "-1.25%",
            "monthlyAvgDeliveryFee": 5.86,
            "dailyAvgDeliveryFee": 5.86,
            "monthlyCumulativeCancelRateScore": "88.24",
            "monthlyMerchantLiabilityRefundRateScore": "91.35",
            "monthlyStockoutRefundRateScore": "98",
            "monthlyNegativeReviewRateScore": "95",
            "monthlyPartialRefundRateScore": "94.85",
            "dailyMeituanRatingScore": "70",
            "dailyElemeRatingScore": "90",
            "monthlyMeituanDeliveryPunctualityRateScore": "100",
            "monthlyElemeTimelyDeliveryRateScore": "100",
            "validReplyWeightingPenalty": "0",
            "monthlyAverageStockRateWeightingPenalty": "0",
            "monthlyAverageTop500StockRateWeightingPenalty": "0",
            "monthlyAverageDirectStockRateWeightingPenalty": "0",
            "newProductComplianceListingWeightingPenalty": "0",
            "expiryManagementWeightingPenalty": "0",
            "inventoryLockWeightingPenalty": "0",
            "monthlyCumulativeHundredOrdersManhourWeightingPenalty": "0",
            "totalScoreWithoutWeightingPenalty": "88.45",
            "monthlyCumulativeMerchantLiabilityRefundRateWeightingPenalty": "0",
            "monthlyCumulativeOutOfStockRefundRateWeightingPenalty": "0",
            "meituanComplexExperienceScoreWeightingPenalty": "0",
            "meituanRatingWeightingPenalty": "0",
            "elemeRatingWeightingPenalty": "0",
            "partialRefundWeightingPenalty": "0",
            "trainingCompletedWeightingPenalty": "0",
            "totalWeightingPenalty": "0"
        },
        {
            "ID": "44839",
            "area": "1区",
            "createDateShow": "2024-09-04",
            "MDShow": "小米之家（解放碑店）",
            "totalScore": 95.12,
            "monthlyCanceledRate": "2.12%",
            "dailyCanceledRate": "2.12%",
            "monthlyMerchantRefundRate": "0.08%",
            "monthlyOosRefundRate": "0.00%",
            "monthlyJdOosRate": "0.00%",
            "monthlyBadReviews": "0",
            "monthlyBadReviewRate": "0.00%",
            "monthlyPartialRefundRate": "0.12%",
            "dailyMeituanRating": "4.9",
            "dailyElemeRating": "4.9",
            "dailyMeituanReplyRate": "95.68%",
            "effectReply": "正常",
            "monthlyMeituanPunctualityRate": "97.85%",
            "monthlyElemeOntimeRate": "96.42%",
            "monthlyJdFulfillmentRate": "94.25%",
            "meituanComprehensiveExperienceDivision": "97.5",
            "monthlyAvgStockRate": "98.75%",
            "monthlyAvgTop500StockRate": "97.86%",
            "monthlyAvgDirectStockRate": "92.15%",
            "dailyTop500StockRate": "97.86%",
            "dailyWarehouseSoldOut": "98",
            "dailyWarehouseStockRate": "99.24%",
            "dailyDirectSoldOut": "12",
            "dailyDirectStockRate": "89.67%",
            "dailyHybridSoldOut": "2",
            "dailyStockAvailability": "98.75%",
            "dailyHybridStockRate": "96.85%",
            "stockNoLocation": "1",
            "expiryManagement": "正常",
            "inventoryLockOrders": "0",
            "trainingCompleted": "正常",
            "monthlyManhourPer100Orders": 6.85,
            "monthlyTotalLoss": -125.75,
            "monthlyTotalLossRate": "-0.68%",
            "monthlyAvgDeliveryFee": 5.42,
            "dailyAvgDeliveryFee": 5.42,
            "monthlyCumulativeCancelRateScore": "92.85",
            "monthlyMerchantLiabilityRefundRateScore": "96.24",
            "monthlyStockoutRefundRateScore": "100",
            "monthlyNegativeReviewRateScore": "100",
            "monthlyPartialRefundRateScore": "97.12",
            "dailyMeituanRatingScore": "95",
            "dailyElemeRatingScore": "95",
            "monthlyMeituanDeliveryPunctualityRateScore": "100",
            "monthlyElemeTimelyDeliveryRateScore": "100",
            "validReplyWeightingPenalty": "0",
            "monthlyAverageStockRateWeightingPenalty": "0",
            "monthlyAverageTop500StockRateWeightingPenalty": "0",
            "monthlyAverageDirectStockRateWeightingPenalty": "0",
            "newProductComplianceListingWeightingPenalty": "0",
            "expiryManagementWeightingPenalty": "0",
            "inventoryLockWeightingPenalty": "0",
            "monthlyCumulativeHundredOrdersManhourWeightingPenalty": "0",
            "totalScoreWithoutWeightingPenalty": "95.12",
            "monthlyCumulativeMerchantLiabilityRefundRateWeightingPenalty": "0",
            "monthlyCumulativeOutOfStockRefundRateWeightingPenalty": "0",
            "meituanComplexExperienceScoreWeightingPenalty": "0",
            "meituanRatingWeightingPenalty": "0",
            "elemeRatingWeightingPenalty": "0",
            "partialRefundWeightingPenalty": "0",
            "trainingCompletedWeightingPenalty": "0",
            "totalWeightingPenalty": "0"
        }
    ]
    
    try:
        # 获取数据库管理器
        db_manager = get_db_manager()
        logger.info(f"📍 数据库路径: {db_manager.base_dir}")
        
        # 插入数据
        inserted_count = db_manager.insert_data(test_data)
        logger.info(f"✅ 成功插入 {inserted_count} 条完整数据")
        
        # 验证数据
        result = db_manager.query_data(page=1, page_size=5)
        logger.info(f"📊 验证数据: 数据库中共有 {result['total']} 条记录")
        
        if result['data']:
            logger.info("📄 样例数据:")
            for i, item in enumerate(result['data'][:3]):
                logger.info(f"   {i+1}. ID={item.get('id', 'N/A')}, rawId={item.get('rawId', 'N/A')}, 门店={item.get('MDShow', 'N/A')}, 得分={item.get('totalScore', 'N/A')}")
        
        logger.info("🎉 完整字段测试数据创建成功！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 创建测试数据失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    create_complete_test_data()
