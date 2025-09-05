export interface Column {
  title: string
  dataIndex: string
  key: string
  width?: number
  fixed?: 'left' | 'right'
  sorter?: boolean
  name?: string
  label?: string
  bizType?: number
}

export interface DataItem {
  ID: string
  area: string
  createDateShow: string
  MDShow: string
  totalScore: number
  monthlyCanceledRate: string
  dailyCanceledRate: string
  monthlyMerchantRefundRate: string
  monthlyOosRefundRate: string
  monthlyJdOosRate: string
  monthlyBadReviews: string
  monthlyBadReviewRate: string
  monthlyPartialRefundRate: string
  dailyMeituanRating: string
  dailyElemeRating: string
  dailyMeituanReplyRate: string
  effectReply: string
  monthlyMeituanPunctualityRate: string
  monthlyElemeOntimeRate: string
  monthlyJdFulfillmentRate: string
  meituanComprehensiveExperienceDivision: string
  monthlyAvgStockRate: string
  monthlyAvgTop500StockRate: string
  monthlyAvgDirectStockRate: string
  dailyTop500StockRate: string
  dailyWarehouseSoldOut: string
  dailyWarehouseStockRate: string
  dailyDirectSoldOut: string
  dailyDirectStockRate: string
  dailyHybridSoldOut: string
  dailyStockAvailability: string
  dailyHybridStockRate: string
  stockNoLocation: string
  expiryManagement: string
  inventoryLockOrders: string
  trainingCompleted: string
  monthlyManhourPer100Orders: number
  monthlyTotalLoss: number
  monthlyTotalLossRate: string
  monthlyAvgDeliveryFee: number
  dailyAvgDeliveryFee: number
  monthlyCumulativeCancelRateScore: string
  monthlyMerchantLiabilityRefundRateScore: string
  monthlyStockoutRefundRateScore: string
  monthlyNegativeReviewRateScore: string
  monthlyPartialRefundRateScore: string
  dailyMeituanRatingScore: string
  dailyElemeRatingScore: string
  monthlyMeituanDeliveryPunctualityRateScore: string
  monthlyElemeTimelyDeliveryRateScore: string
  validReplyWeightingPenalty: string
  monthlyAverageStockRateWeightingPenalty: string
  monthlyAverageTop500StockRateWeightingPenalty: string
  monthlyAverageDirectStockRateWeightingPenalty: string
  newProductComplianceListingWeightingPenalty: string
  expiryManagementWeightingPenalty: string
  inventoryLockWeightingPenalty: string
  monthlyCumulativeHundredOrdersManhourWeightingPenalty: string
  totalScoreWithoutWeightingPenalty: string
  monthlyCumulativeMerchantLiabilityRefundRateWeightingPenalty: string
  monthlyCumulativeOutOfStockRefundRateWeightingPenalty: string
  meituanComplexExperienceScoreWeightingPenalty: string
  meituanRatingWeightingPenalty: string
  elemeRatingWeightingPenalty: string
  partialRefundWeightingPenalty: string
  trainingCompletedWeightingPenalty: string
  totalWeightingPenalty: string
}

export interface SearchForm {
  area?: string
  MDShow?: string
  dateRange?: [string, string]
}
