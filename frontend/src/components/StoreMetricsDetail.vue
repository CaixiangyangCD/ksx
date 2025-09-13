<template>
  <a-modal
    v-model:open="visible"
    :title="`${storeName} - 指标数据详情`"
    :width="1400"
    @cancel="handleCancel"
    :footer="null"
    :z-index="2000"
  >
    <div class="store-metrics-detail">
      <!-- 指标数据表格 -->
      <div class="metrics-table">
        <a-table
          :columns="columns"
          :data-source="tableData"
          :pagination="false"
          :scroll="{ x: 1200, y: 500 }"
          size="small"
          bordered
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'metric_name'">
              <span style="font-weight: 500; color: #1890ff;">{{ record.metric_name }}</span>
            </template>
            <template v-else-if="isDateColumn(column.key)">
              <span :style="{ 
                color: record[column.key] !== null && record[column.key] !== undefined ? '#262626' : '#8c8c8c',
                fontSize: '12px'
              }">
                {{ formatDataValue(record[column.key]) }}
              </span>
            </template>
          </template>
        </a-table>
      </div>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface MetricData {
  metric_name: string
  daily_data: Record<string, any>
  total_days: number
  row_index: number
}

interface Props {
  open: boolean
  storeName: string
  storeData: Record<string, MetricData>
  fileInfo: any
}

interface Emits {
  (e: 'update:open', value: boolean): void
}

const props = withDefaults(defineProps<Props>(), {
  open: false,
  storeName: '',
  storeData: () => ({}),
  fileInfo: () => ({})
})

const emit = defineEmits<Emits>()

// 响应式数据
const visible = computed({
  get: () => props.open,
  set: (value) => emit('update:open', value)
})

// 获取所有日期
const getAllDates = () => {
  const allDates = new Set<string>()
  Object.values(props.storeData).forEach(metric => {
    Object.keys(metric.daily_data || {}).forEach(date => {
      allDates.add(date)
    })
  })
  return Array.from(allDates).sort((a, b) => {
    const aNum = parseInt(a.replace('日', ''))
    const bNum = parseInt(b.replace('日', ''))
    return aNum - bNum
  })
}


// 动态生成表格列
const columns = computed(() => {
  const baseColumns = [
    {
      title: '指标名称',
      dataIndex: 'metric_name',
      key: 'metric_name',
      width: 200,
      fixed: 'left'
    }
  ]
  
  const dateColumns = getAllDates().map(date => ({
    title: date,
    dataIndex: date,
    key: date,
    width: 100,
    align: 'center' as const
  }))
  
  return [...baseColumns, ...dateColumns]
})

// 生成表格数据
const tableData = computed(() => {
  const dates = getAllDates()
  
  return Object.values(props.storeData).map(metric => {
    const row: any = {
      key: metric.metric_name,
      metric_name: metric.metric_name
    }
    
    // 为每个日期添加数据
    dates.forEach(date => {
      row[date] = metric.daily_data[date]
    })
    
    return row
  })
})

// 判断是否为日期列
const isDateColumn = (key: string) => {
  return key !== 'metric_name' && key !== 'key'
}

// 格式化数据值
const formatDataValue = (value: any) => {
  if (value === null || value === undefined) {
    return '-'
  }
  
  if (typeof value === 'number') {
    if (value < 1 && value > 0) {
      return `${(value * 100).toFixed(2)}%`
    } else if (value >= 1 && value <= 5) {
      // 评分数据（1-5分）
      return value.toFixed(1)
    } else {
      return value.toFixed(4)
    }
  }
  
  return String(value)
}

// 取消
const handleCancel = () => {
  visible.value = false
}
</script>

<style scoped>
.store-metrics-detail {
  max-height: 600px;
  overflow-y: auto;
}

.metrics-table {
  margin-bottom: 20px;
}

.ant-table-tbody > tr > td {
  padding: 6px 8px;
}

.ant-table-thead > tr > th {
  background-color: #fafafa;
  font-weight: 500;
}

.ant-table-thead > tr > th:first-child {
  background-color: #e6f7ff;
}
</style>
