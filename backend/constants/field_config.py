"""
字段配置常量
包含所有数据字段的配置信息
"""

# 字段配置和中文名称映射
FIELD_CONFIG = {
    "area": {"name": "区域", "comment": "门店所属区域"},
    "createDateShow": {"name": "创建日期", "comment": "数据创建日期"},
    "MDShow": {"name": "门店名称", "comment": "门店显示名称"},
    "totalScore": {"name": "总分", "comment": "门店综合评分"},
    "monthlyCanceledRate": {"name": "月度取消率", "comment": "月度订单取消率"},
    "dailyCanceledRate": {"name": "日取消率", "comment": "日订单取消率"},
    "monthlyMerchantRefundRate": {"name": "月度商家退款率", "comment": "月度商家责任退款率"},
    "monthlyOosRefundRate": {"name": "月度缺货退款率", "comment": "月度缺货退款率"},
    "monthlyJdOosRate": {"name": "月度京东缺货率", "comment": "月度京东缺货率"},
    "monthlyBadReviews": {"name": "月度差评数", "comment": "月度差评数量"},
    "monthlyBadReviewRate": {"name": "月度差评率", "comment": "月度差评率"},
    "monthlyPartialRefundRate": {"name": "月度部分退款率", "comment": "月度部分退款率"},
    "dailyMeituanRating": {"name": "美团评分", "comment": "美团平台日评分"},
    "dailyElemeRating": {"name": "饿了么评分", "comment": "饿了么平台日评分"},
    "dailyMeituanReplyRate": {"name": "美团回复率", "comment": "美团平台回复率"},
    "effectReply": {"name": "有效回复", "comment": "有效回复状态"},
    "monthlyMeituanPunctualityRate": {"name": "美团准时率", "comment": "美团月度准时送达率"},
    "monthlyElemeOntimeRate": {"name": "饿了么准时率", "comment": "饿了么月度准时送达率"},
    "monthlyJdFulfillmentRate": {"name": "京东履约率", "comment": "京东月度履约率"},
    "meituanComprehensiveExperienceDivision": {"name": "美团综合体验分", "comment": "美团综合体验评分"},
    "monthlyAvgStockRate": {"name": "月度平均库存率", "comment": "月度平均库存率"},
    "monthlyAvgTop500StockRate": {"name": "月度TOP500库存率", "comment": "月度TOP500商品库存率"},
    "monthlyAvgDirectStockRate": {"name": "月度直营库存率", "comment": "月度直营商品库存率"},
    "dailyTop500StockRate": {"name": "日TOP500库存率", "comment": "日TOP500商品库存率"},
    "dailyWarehouseSoldOut": {"name": "日仓库售罄数", "comment": "日仓库售罄商品数"},
    "dailyWarehouseStockRate": {"name": "日仓库库存率", "comment": "日仓库库存率"},
    "dailyDirectSoldOut": {"name": "日直营售罄数", "comment": "日直营售罄商品数"},
    "dailyDirectStockRate": {"name": "日直营库存率", "comment": "日直营库存率"},
    "dailyHybridSoldOut": {"name": "日混合售罄数", "comment": "日混合售罄商品数"},
    "dailyStockAvailability": {"name": "日库存可用率", "comment": "日库存可用率"},
    "dailyHybridStockRate": {"name": "日混合库存率", "comment": "日混合库存率"},
    "stockNoLocation": {"name": "无位置库存数", "comment": "无位置库存商品数"},
    "expiryManagement": {"name": "保质期管理", "comment": "保质期管理状态"},
    "inventoryLockOrders": {"name": "库存锁定订单", "comment": "库存锁定订单数"},
    "trainingCompleted": {"name": "培训完成", "comment": "培训完成状态"},
    "monthlyManhourPer100Orders": {"name": "月度百单工时", "comment": "月度每百单工时"},
    "monthlyTotalLoss": {"name": "月度总损失", "comment": "月度总损失金额"},
    "monthlyTotalLossRate": {"name": "月度总损失率", "comment": "月度总损失率"},
    "monthlyAvgDeliveryFee": {"name": "月度平均配送费", "comment": "月度平均配送费"},
    "dailyAvgDeliveryFee": {"name": "日平均配送费", "comment": "日平均配送费"},
    "monthlyCumulativeCancelRateScore": {"name": "月度累计取消率得分", "comment": "月度累计取消率得分"},
    "monthlyMerchantLiabilityRefundRateScore": {"name": "月度商家责任退款率得分", "comment": "月度商家责任退款率得分"},
    "monthlyStockoutRefundRateScore": {"name": "月度缺货退款率得分", "comment": "月度缺货退款率得分"},
    "monthlyNegativeReviewRateScore": {"name": "月度差评率得分", "comment": "月度差评率得分"},
    "monthlyPartialRefundRateScore": {"name": "月度部分退款率得分", "comment": "月度部分退款率得分"},
    "dailyMeituanRatingScore": {"name": "美团评分得分", "comment": "美团评分得分"},
    "dailyElemeRatingScore": {"name": "饿了么评分得分", "comment": "饿了么评分得分"},
    "monthlyMeituanDeliveryPunctualityRateScore": {"name": "美团配送准时率得分", "comment": "美团配送准时率得分"},
    "monthlyElemeTimelyDeliveryRateScore": {"name": "饿了么及时配送率得分", "comment": "饿了么及时配送率得分"},
    "validReplyWeightingPenalty": {"name": "有效回复权重惩罚", "comment": "有效回复权重惩罚"},
    "monthlyAverageStockRateWeightingPenalty": {"name": "月度平均库存率权重惩罚", "comment": "月度平均库存率权重惩罚"},
    "monthlyAverageTop500StockRateWeightingPenalty": {"name": "月度TOP500库存率权重惩罚", "comment": "月度TOP500库存率权重惩罚"},
    "monthlyAverageDirectStockRateWeightingPenalty": {"name": "月度直营库存率权重惩罚", "comment": "月度直营库存率权重惩罚"},
    "newProductComplianceListingWeightingPenalty": {"name": "新品合规上架权重惩罚", "comment": "新品合规上架权重惩罚"},
    "expiryManagementWeightingPenalty": {"name": "保质期管理权重惩罚", "comment": "保质期管理权重惩罚"},
    "inventoryLockWeightingPenalty": {"name": "库存锁定权重惩罚", "comment": "库存锁定权重惩罚"},
    "monthlyCumulativeHundredOrdersManhourWeightingPenalty": {"name": "月度累计百单工时权重惩罚", "comment": "月度累计百单工时权重惩罚"},
    "totalScoreWithoutWeightingPenalty": {"name": "无权重惩罚总分", "comment": "无权重惩罚总分"},
    "monthlyCumulativeMerchantLiabilityRefundRateWeightingPenalty": {"name": "月度累计商家责任退款率权重惩罚", "comment": "月度累计商家责任退款率权重惩罚"},
    "monthlyCumulativeOutOfStockRefundRateWeightingPenalty": {"name": "月度累计缺货退款率权重惩罚", "comment": "月度累计缺货退款率权重惩罚"},
    "meituanComplexExperienceScoreWeightingPenalty": {"name": "美团综合体验分权重惩罚", "comment": "美团综合体验分权重惩罚"},
    "meituanRatingWeightingPenalty": {"name": "美团评分权重惩罚", "comment": "美团评分权重惩罚"},
    "elemeRatingWeightingPenalty": {"name": "饿了么评分权重惩罚", "comment": "饿了么评分权重惩罚"},
    "partialRefundWeightingPenalty": {"name": "部分退款权重惩罚", "comment": "部分退款权重惩罚"},
    "trainingCompletedWeightingPenalty": {"name": "培训完成权重惩罚", "comment": "培训完成权重惩罚"},
    "totalWeightingPenalty": {"name": "总权重惩罚", "comment": "总权重惩罚"}
}

# Excel中常见的指标名称映射（用于兼容不同的Excel格式）
EXCEL_METRICS_MAPPING = {
    # 取消率相关
    "月累计取消率": "monthlyCanceledRate",
    "当日取消率": "dailyCanceledRate",
    "月累计商责退款率": "monthlyMerchantRefundRate",
    "月累计部分退款率": "monthlyPartialRefundRate",
    
    # 评分相关
    "当日美团评分": "dailyMeituanRating",
    "当日饿了么评分": "dailyElemeRating",
    "月累计美团配送准时率": "monthlyMeituanPunctualityRate",
    "月累计饿了么及时送达率": "monthlyElemeOntimeRate",
    
    # 库存相关
    "月平均有货率": "monthlyAvgStockRate",
    "月平均TOP500有货率": "monthlyAvgTop500StockRate",
    "月平均直送直配有货率": "monthlyAvgDirectStockRate",
    
    # 其他常见指标
    "月累计缺货退款率": "monthlyOosRefundRate",
    "月累计差评率": "monthlyBadReviewRate",
    "月累计差评总数": "monthlyBadReviews",
    "当日美团近7日首条消息1分钟人工回复率": "dailyMeituanReplyRate",
    "有效回复": "effectReply",
    "月累计京东秒送订单履约率": "monthlyJdFulfillmentRate",
    "美团综合体体验分": "meituanComprehensiveExperienceDivision"
}

def get_field_display_name(field_key: str) -> str:
    """获取字段的显示名称"""
    return FIELD_CONFIG.get(field_key, {}).get("name", field_key)

def get_field_comment(field_key: str) -> str:
    """获取字段的注释"""
    return FIELD_CONFIG.get(field_key, {}).get("comment", "")

def get_all_field_keys() -> list:
    """获取所有字段键名"""
    return list(FIELD_CONFIG.keys())

def get_excel_metric_key(excel_metric_name: str) -> str:
    """根据Excel中的指标名称获取对应的字段键名"""
    return EXCEL_METRICS_MAPPING.get(excel_metric_name, excel_metric_name)
