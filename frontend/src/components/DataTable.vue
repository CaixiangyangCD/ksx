<template>
  <div class="data-table">
    <a-table
      :columns="columns"
      :data-source="dataSource"
      :pagination="pagination"
      :loading="loading"
      :scroll="{ x: 2000 }"
      size="small"
      bordered
      @change="handleTableChange"
      class="custom-table"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'MDShow'">
          <span v-html="record.MDShow"></span>
        </template>
        <template v-else-if="column.key === 'totalScore'">
          <a-tag :color="getScoreColor(record.totalScore)">
            {{ record.totalScore }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'effectReply'">
          <a-tag :color="record.effectReply === '正常' ? 'green' : 'red'">
            {{ record.effectReply }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'expiryManagement'">
          <a-tag :color="record.expiryManagement === '正常' ? 'green' : 'red'">
            {{ record.expiryManagement }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'trainingCompleted'">
          <a-tag :color="record.trainingCompleted === '正常' ? 'green' : 'red'">
            {{ record.trainingCompleted }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'monthlyTotalLoss'">
          <span :style="{ color: record.monthlyTotalLoss >= 0 ? 'red' : 'green' }">
            {{ record.monthlyTotalLoss.toFixed(2) }}
          </span>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DataItem, Column } from '../types'

interface Props {
  dataSource: DataItem[]
  loading: boolean
  pagination: {
    current: number
    pageSize: number
    total: number
  }
}

interface Emits {
  (e: 'change', pagination: any, filters: any, sorter: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const columns: Column[] = [
  {
    title: '自增ID',
    dataIndex: 'id',
    key: 'id',
    width: 80,
    fixed: 'left'
  },
  {
    title: '原始ID',
    dataIndex: 'rawId',
    key: 'rawId',
    width: 100,
    fixed: 'left'
  },
  {
    title: '区域',
    dataIndex: 'area',
    key: 'area',
    width: 80,
    fixed: 'left'
  },
  {
    title: '日期',
    dataIndex: 'createDateShow',
    key: 'createDateShow',
    width: 100,
    fixed: 'left'
  },
  {
    title: '门店名称',
    dataIndex: 'MDShow',
    key: 'MDShow',
    width: 200,
    fixed: 'left'
  },
  {
    title: '最终得分',
    dataIndex: 'totalScore',
    key: 'totalScore',
    width: 100,
    sorter: true
  },
  {
    title: '月累计取消率',
    dataIndex: 'monthlyCanceledRate',
    key: 'monthlyCanceledRate',
    width: 120
  },
  {
    title: '当日取消率',
    dataIndex: 'dailyCanceledRate',
    key: 'dailyCanceledRate',
    width: 120
  },
  {
    title: '月累计商责退单率',
    dataIndex: 'monthlyMerchantRefundRate',
    key: 'monthlyMerchantRefundRate',
    width: 150
  },
  {
    title: '月累计缺货退款率',
    dataIndex: 'monthlyOosRefundRate',
    key: 'monthlyOosRefundRate',
    width: 150
  },
  {
    title: '月累计京东秒送缺货出率',
    dataIndex: 'monthlyJdOosRate',
    key: 'monthlyJdOosRate',
    width: 180
  },
  {
    title: '月累计差评总数',
    dataIndex: 'monthlyBadReviews',
    key: 'monthlyBadReviews',
    width: 130
  },
  {
    title: '月累计差评率',
    dataIndex: 'monthlyBadReviewRate',
    key: 'monthlyBadReviewRate',
    width: 130
  },
  {
    title: '月累计部分退款率',
    dataIndex: 'monthlyPartialRefundRate',
    key: 'monthlyPartialRefundRate',
    width: 150
  },
  {
    title: '当日美团评分',
    dataIndex: 'dailyMeituanRating',
    key: 'dailyMeituanRating',
    width: 130
  },
  {
    title: '当日饿了么评分',
    dataIndex: 'dailyElemeRating',
    key: 'dailyElemeRating',
    width: 130
  },
  {
    title: '当日美团近7日首条消息1分钟人工回复率',
    dataIndex: 'dailyMeituanReplyRate',
    key: 'dailyMeituanReplyRate',
    width: 200
  },
  {
    title: '有效回复',
    dataIndex: 'effectReply',
    key: 'effectReply',
    width: 100
  },
  {
    title: '月累计美团配送准时率',
    dataIndex: 'monthlyMeituanPunctualityRate',
    key: 'monthlyMeituanPunctualityRate',
    width: 180
  },
  {
    title: '月累计饿了么及时送达率',
    dataIndex: 'monthlyElemeOntimeRate',
    key: 'monthlyElemeOntimeRate',
    width: 180
  },
  {
    title: '月累计京东秒送订单履约率',
    dataIndex: 'monthlyJdFulfillmentRate',
    key: 'monthlyJdFulfillmentRate',
    width: 180
  },
  {
    title: '美团综合体体验分',
    dataIndex: 'meituanComprehensiveExperienceDivision',
    key: 'meituanComprehensiveExperienceDivision',
    width: 150
  },
  {
    title: '月平均有货率',
    dataIndex: 'monthlyAvgStockRate',
    key: 'monthlyAvgStockRate',
    width: 130
  },
  {
    title: '月平均TOP500有货率',
    dataIndex: 'monthlyAvgTop500StockRate',
    key: 'monthlyAvgTop500StockRate',
    width: 160
  },
  {
    title: '月平均直配直送有货率',
    dataIndex: 'monthlyAvgDirectStockRate',
    key: 'monthlyAvgDirectStockRate',
    width: 160
  },
  {
    title: '当日TOP500有货率',
    dataIndex: 'dailyTop500StockRate',
    key: 'dailyTop500StockRate',
    width: 150
  },
  {
    title: '当日仓配售罄数',
    dataIndex: 'dailyWarehouseSoldOut',
    key: 'dailyWarehouseSoldOut',
    width: 130
  },
  {
    title: '当日仓配有货率',
    dataIndex: 'dailyWarehouseStockRate',
    key: 'dailyWarehouseStockRate',
    width: 130
  },
  {
    title: '当日直送售罄数',
    dataIndex: 'dailyDirectSoldOut',
    key: 'dailyDirectSoldOut',
    width: 130
  },
  {
    title: '当日直送有货率',
    dataIndex: 'dailyDirectStockRate',
    key: 'dailyDirectStockRate',
    width: 130
  },
  {
    title: '当日直配售罄数',
    dataIndex: 'dailyHybridSoldOut',
    key: 'dailyHybridSoldOut',
    width: 130
  },
  {
    title: '当日有货率',
    dataIndex: 'dailyStockAvailability',
    key: 'dailyStockAvailability',
    width: 120
  },
  {
    title: '当日直配有货率',
    dataIndex: 'dailyHybridStockRate',
    key: 'dailyHybridStockRate',
    width: 140
  },
  {
    title: '有库存无库位数',
    dataIndex: 'stockNoLocation',
    key: 'stockNoLocation',
    width: 130
  },
  {
    title: '效期管理',
    dataIndex: 'expiryManagement',
    key: 'expiryManagement',
    width: 100
  },
  {
    title: '库存锁定单数',
    dataIndex: 'inventoryLockOrders',
    key: 'inventoryLockOrders',
    width: 120
  },
  {
    title: '培训完结',
    dataIndex: 'trainingCompleted',
    key: 'trainingCompleted',
    width: 100
  },
  {
    title: '月累计百单编制工时',
    dataIndex: 'monthlyManhourPer100Orders',
    key: 'monthlyManhourPer100Orders',
    width: 150
  },
  {
    title: '月累计综合损溢额',
    dataIndex: 'monthlyTotalLoss',
    key: 'monthlyTotalLoss',
    width: 150
  },
  {
    title: '月累计综合损溢率',
    dataIndex: 'monthlyTotalLossRate',
    key: 'monthlyTotalLossRate',
    width: 150
  },
  {
    title: '本月累计单均配送费',
    dataIndex: 'monthlyAvgDeliveryFee',
    key: 'monthlyAvgDeliveryFee',
    width: 150
  },
  {
    title: '当日单均配送费',
    dataIndex: 'dailyAvgDeliveryFee',
    key: 'dailyAvgDeliveryFee',
    width: 130
  }
]

const getScoreColor = (score: number) => {
  if (score >= 95) return 'green'
  if (score >= 90) return 'blue'
  if (score >= 80) return 'orange'
  return 'red'
}

const handleTableChange = (pagination: any, filters: any, sorter: any) => {
  emit('change', pagination, filters, sorter)
}
</script>

<style scoped>
.data-table {
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* 自定义表格样式 */
.custom-table {
  --ant-table-border-color: #e8e8e8;
  --ant-table-header-bg: #fafafa;
}

/* 美化分页器样式 */
:deep(.ant-pagination) {
  margin: 16px 0;
  text-align: center;
}

:deep(.ant-pagination .ant-pagination-item) {
  border-radius: 6px;
  border: 1px solid #d9d9d9;
  margin: 0 4px;
  transition: all 0.3s ease;
}

:deep(.ant-pagination .ant-pagination-item:hover) {
  border-color: #1890ff;
  color: #1890ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.15);
}

:deep(.ant-pagination .ant-pagination-item-active) {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  border-color: #1890ff;
  color: white;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);
}

:deep(.ant-pagination .ant-pagination-item-active:hover) {
  background: linear-gradient(135deg, #40a9ff 0%, #69c0ff 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.4);
}

:deep(.ant-pagination .ant-pagination-prev),
:deep(.ant-pagination .ant-pagination-next) {
  border-radius: 6px;
  border: 1px solid #d9d9d9;
  margin: 0 4px;
  transition: all 0.3s ease;
}

:deep(.ant-pagination .ant-pagination-prev:hover),
:deep(.ant-pagination .ant-pagination-next:hover) {
  border-color: #1890ff;
  color: #1890ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.15);
}

:deep(.ant-pagination .ant-pagination-jump-prev),
:deep(.ant-pagination .ant-pagination-jump-next) {
  border-radius: 6px;
  border: 1px solid #d9d9d9;
  margin: 0 4px;
  transition: all 0.3s ease;
}

:deep(.ant-pagination .ant-pagination-jump-prev:hover),
:deep(.ant-pagination .ant-pagination-jump-next:hover) {
  border-color: #1890ff;
  color: #1890ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.15);
}

:deep(.ant-pagination .ant-pagination-options) {
  margin-left: 16px;
}

:deep(.ant-pagination .ant-pagination-options-quick-jumper) {
  margin-left: 8px;
}

:deep(.ant-pagination .ant-pagination-options-quick-jumper input) {
  border-radius: 6px;
  border: 1px solid #d9d9d9;
  transition: all 0.3s ease;
}

:deep(.ant-pagination .ant-pagination-options-quick-jumper input:focus) {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

:deep(.ant-pagination .ant-select) {
  border-radius: 6px;
}

:deep(.ant-pagination .ant-select .ant-select-selector) {
  border-radius: 6px;
  border: 1px solid #d9d9d9;
  transition: all 0.3s ease;
}

:deep(.ant-pagination .ant-select:hover .ant-select-selector) {
  border-color: #1890ff;
}

:deep(.ant-pagination .ant-select-focused .ant-select-selector) {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

/* 分页器总数显示样式 */
:deep(.ant-pagination .ant-pagination-total-text) {
  color: #666;
  font-weight: 500;
  margin-right: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  :deep(.ant-pagination) {
    text-align: center;
  }
  
  :deep(.ant-pagination .ant-pagination-options) {
    margin-left: 8px;
    margin-top: 8px;
  }
  
  :deep(.ant-pagination .ant-pagination-total-text) {
    display: block;
    margin-bottom: 8px;
    text-align: center;
  }
}
</style>
