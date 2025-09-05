import { DataItem } from '../types'

// 生成126条假数据
export const generateMockData = (): DataItem[] => {
  const areas = ['1区', '2区', '3区', '4区', '5区']
  const storeNames = [
    '京东便利店（城东店）',
    '京东便利店（城西店）',
    '京东便利店（城南店）',
    '京东便利店（城北店）',
    '京东便利店（中心店）',
    '京东便利店（东湖店）',
    '京东便利店（西湖店）',
    '京东便利店（南湖店）',
    '京东便利店（北湖店）',
    '京东便利店（高新店）',
    '京东便利店（经开店）',
    '京东便利店（滨湖店）',
    '京东便利店（蜀山店）',
    '京东便利店（包河店）',
    '京东便利店（瑶海店）',
    '京东便利店（庐阳店）',
    '京东便利店（肥东店）',
    '京东便利店（肥西店）',
    '京东便利店（长丰店）',
    '京东便利店（庐江店）',
    '京东便利店（巢湖店）',
    '京东便利店（无为店）',
    '京东便利店（和县店）',
    '京东便利店（含山店）',
    '京东便利店（当涂店）',
    '京东便利店（芜湖店）'
  ]

  const mockData: DataItem[] = []

  for (let i = 1; i <= 126; i++) {
    const area = areas[Math.floor(Math.random() * areas.length)]
    const storeName = storeNames[Math.floor(Math.random() * storeNames.length)]
    const storeCode = `S${String(i).padStart(3, '0')}`
    
    const totalScore = Math.floor(Math.random() * 20) + 80 // 80-100分
    const monthlyCanceledRate = (Math.random() * 5).toFixed(2) + '%'
    const dailyCanceledRate = (Math.random() * 5).toFixed(2) + '%'
    const monthlyMerchantRefundRate = (Math.random() * 1).toFixed(2) + '%'
    const monthlyOosRefundRate = (Math.random() * 0.5).toFixed(2) + '%'
    const monthlyJdOosRate = (Math.random() * 0.5).toFixed(2) + '%'
    const monthlyBadReviews = Math.floor(Math.random() * 5).toString()
    const monthlyBadReviewRate = (Math.random() * 2).toFixed(2) + '%'
    const monthlyPartialRefundRate = (Math.random() * 1).toFixed(2) + '%'
    const dailyMeituanRating = (Math.random() * 1 + 4).toFixed(1)
    const dailyElemeRating = (Math.random() * 1 + 4).toFixed(1)
    const dailyMeituanReplyRate = (Math.random() * 20 + 80).toFixed(2) + '%'
    const monthlyMeituanPunctualityRate = (Math.random() * 10 + 90).toFixed(2) + '%'
    const monthlyElemeOntimeRate = (Math.random() * 10 + 90).toFixed(2) + '%'
    const monthlyJdFulfillmentRate = (Math.random() * 20 + 80).toFixed(2) + '%'
    const meituanComprehensiveExperienceDivision = (Math.random() * 5 + 90).toFixed(1)
    const monthlyAvgStockRate = (Math.random() * 5 + 95).toFixed(2) + '%'
    const monthlyAvgTop500StockRate = (Math.random() * 5 + 95).toFixed(2) + '%'
    const monthlyAvgDirectStockRate = (Math.random() * 20 + 80).toFixed(2) + '%'
    const dailyTop500StockRate = (Math.random() * 5 + 95).toFixed(2) + '%'
    const dailyWarehouseSoldOut = Math.floor(Math.random() * 200).toString()
    const dailyWarehouseStockRate = (Math.random() * 5 + 95).toFixed(2) + '%'
    const dailyDirectSoldOut = Math.floor(Math.random() * 50).toString()
    const dailyDirectStockRate = (Math.random() * 20 + 80).toFixed(2) + '%'
    const dailyHybridSoldOut = Math.floor(Math.random() * 20).toString()
    const dailyStockAvailability = (Math.random() * 5 + 95).toFixed(2) + '%'
    const dailyHybridStockRate = (Math.random() * 10 + 90).toFixed(2) + '%'
    const stockNoLocation = Math.floor(Math.random() * 10).toString()
    const monthlyManhourPer100Orders = Math.random() * 5 + 5
    const monthlyTotalLoss = Math.random() * 1000 - 500
    const monthlyTotalLossRate = (Math.random() * 4 - 2).toFixed(2) + '%'
    const monthlyAvgDeliveryFee = Math.random() * 3 + 4
    const dailyAvgDeliveryFee = Math.random() * 3 + 4

    const item: DataItem = {
      ID: (44837 + i).toString(),
      area,
      createDateShow: `2025-${String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')}-${String(Math.floor(Math.random() * 28) + 1).padStart(2, '0')}`,
      MDShow: `<font>[${storeCode}]${storeName}</font>`,
      totalScore,
      monthlyCanceledRate,
      dailyCanceledRate,
      monthlyMerchantRefundRate,
      monthlyOosRefundRate,
      monthlyJdOosRate,
      monthlyBadReviews,
      monthlyBadReviewRate,
      monthlyPartialRefundRate,
      dailyMeituanRating,
      dailyElemeRating,
      dailyMeituanReplyRate,
      effectReply: Math.random() > 0.1 ? '正常' : '异常',
      monthlyMeituanPunctualityRate,
      monthlyElemeOntimeRate,
      monthlyJdFulfillmentRate,
      meituanComprehensiveExperienceDivision,
      monthlyAvgStockRate,
      monthlyAvgTop500StockRate,
      monthlyAvgDirectStockRate,
      dailyTop500StockRate,
      dailyWarehouseSoldOut,
      dailyWarehouseStockRate,
      dailyDirectSoldOut,
      dailyDirectStockRate,
      dailyHybridSoldOut,
      dailyStockAvailability,
      dailyHybridStockRate,
      stockNoLocation,
      expiryManagement: Math.random() > 0.1 ? '正常' : '异常',
      inventoryLockOrders: Math.floor(Math.random() * 5).toString(),
      trainingCompleted: Math.random() > 0.1 ? '正常' : '异常',
      monthlyManhourPer100Orders,
      monthlyTotalLoss,
      monthlyTotalLossRate,
      monthlyAvgDeliveryFee,
      dailyAvgDeliveryFee,
      monthlyCumulativeCancelRateScore: (Math.random() * 20 + 80).toFixed(0),
      monthlyMerchantLiabilityRefundRateScore: (Math.random() * 20 + 80).toFixed(0),
      monthlyStockoutRefundRateScore: (Math.random() * 20 + 80).toFixed(0),
      monthlyNegativeReviewRateScore: (Math.random() * 20 + 80).toFixed(0),
      monthlyPartialRefundRateScore: (Math.random() * 20 + 80).toFixed(0),
      dailyMeituanRatingScore: (Math.random() * 40 + 60).toFixed(0),
      dailyElemeRatingScore: (Math.random() * 40 + 60).toFixed(0),
      monthlyMeituanDeliveryPunctualityRateScore: (Math.random() * 20 + 80).toFixed(0),
      monthlyElemeTimelyDeliveryRateScore: (Math.random() * 20 + 80).toFixed(0),
      validReplyWeightingPenalty: Math.random() > 0.8 ? Math.floor(Math.random() * 5).toString() : '0',
      monthlyAverageStockRateWeightingPenalty: Math.random() > 0.8 ? Math.floor(Math.random() * 5).toString() : '0',
      monthlyAverageTop500StockRateWeightingPenalty: Math.random() > 0.8 ? Math.floor(Math.random() * 5).toString() : '0',
      monthlyAverageDirectStockRateWeightingPenalty: Math.random() > 0.8 ? Math.floor(Math.random() * 5).toString() : '0',
      newProductComplianceListingWeightingPenalty: Math.random() > 0.8 ? Math.floor(Math.random() * 5).toString() : '0',
      expiryManagementWeightingPenalty: Math.random() > 0.8 ? Math.floor(Math.random() * 5).toString() : '0',
      inventoryLockWeightingPenalty: Math.random() > 0.8 ? Math.floor(Math.random() * 5).toString() : '0',
      monthlyCumulativeHundredOrdersManhourWeightingPenalty: Math.random() > 0.8 ? Math.floor(Math.random() * 5).toString() : '0',
      totalScoreWithoutWeightingPenalty: totalScore.toFixed(2),
      monthlyCumulativeMerchantLiabilityRefundRateWeightingPenalty: Math.random() > 0.8 ? Math.floor(Math.random() * 5).toString() : '0',
      monthlyCumulativeOutOfStockRefundRateWeightingPenalty: Math.random() > 0.8 ? Math.floor(Math.random() * 5).toString() : '0',
      meituanComplexExperienceScoreWeightingPenalty: Math.random() > 0.8 ? Math.floor(Math.random() * 5).toString() : '0',
      meituanRatingWeightingPenalty: Math.random() > 0.8 ? Math.floor(Math.random() * 5).toString() : '0',
      elemeRatingWeightingPenalty: Math.random() > 0.8 ? Math.floor(Math.random() * 5).toString() : '0',
      partialRefundWeightingPenalty: Math.random() > 0.8 ? Math.floor(Math.random() * 5).toString() : '0',
      trainingCompletedWeightingPenalty: Math.random() > 0.8 ? Math.floor(Math.random() * 5).toString() : '0',
      totalWeightingPenalty: Math.random() > 0.8 ? Math.floor(Math.random() * 10).toString() : '0'
    }

    mockData.push(item)
  }

  return mockData
}
