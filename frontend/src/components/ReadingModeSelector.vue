<template>
  <a-modal
    :open="visible"
    @update:open="(value) => emit('update:visible', value)"
    title="选择读取模式"
    :width="900"
    @ok="handleConfirm"
    @cancel="handleCancel"
    :confirm-loading="loading"
    :ok-button-props="{ disabled: !canConfirm }"
    ok-text="确认选择"
    cancel-text="取消"
    :z-index="1100"
    :mask-closable="false"
  >
    <div class="reading-mode-selector">
    <div class="header">
      <h3>选择读取模式</h3>
      <p class="description">请选择适合当前情况的Excel数据读取方式</p>
      
    </div>

    <div class="mode-options">
      <div 
        v-for="(mode, key) in readingModes" 
        :key="key"
        class="mode-card"
        :class="{ 'selected': selectedMode === key }"
        @click="selectMode(key)"
      >
        <div class="mode-header">
          <div class="mode-title">
            <input 
              type="radio" 
              :value="key" 
              v-model="selectedMode"
              class="mode-radio"
            />
            <h4>{{ mode.title }}</h4>
          </div>
          <div class="mode-badge" :class="key">
            {{ key === 'incremental' ? '推荐' : '完整' }}
          </div>
        </div>
        
        <p class="mode-description">{{ mode.description }}</p>
        
        <div class="mode-advantages">
          <h5>优势：</h5>
          <ul>
            <li v-for="advantage in mode.advantages" :key="advantage">
              {{ advantage }}
            </li>
          </ul>
        </div>
        
        <div class="mode-recommended">
          <h5>推荐场景：</h5>
          <ul>
            <li v-for="scenario in mode.recommended_for" :key="scenario">
              {{ scenario }}
            </li>
          </ul>
        </div>
      </div>
    </div>


    <div class="tracking-info" v-if="selectedMode === 'incremental' && trackingData.length > 0">
      <h4>门店数据状态</h4>
      <div class="tracking-summary">
        <p>已跟踪 {{ trackingData.length }} 个门店的数据</p>
        <a-button type="link" @click="showTrackingDetails = !showTrackingDetails">
          {{ showTrackingDetails ? '隐藏详情' : '查看详情' }}
        </a-button>
      </div>
      
      <div v-if="showTrackingDetails" class="tracking-details">
        <a-table 
          :columns="trackingColumns"
          :data-source="trackingData"
          :pagination="{ pageSize: 5 }"
          size="small"
        />
      </div>
    </div>

  </div>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const API_BASE_URL = "http://localhost:18888"

interface ReadingMode {
  title: string
  description: string
  advantages: string[]
  recommended_for: string[]
}

interface TrackingData {
  store_name: string
  database_month: string
  latest_date: string
  total_records: number
  updated_at: string
}

interface Props {
  visible: boolean
  excelFilename?: string
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'confirm', config: { mode: string, month?: string }): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const selectedMode = ref<string>('incremental')
const selectedMonth = ref<string>('')
const trackingData = ref<TrackingData[]>([])
const showTrackingDetails = ref(false)
const readingModes = ref<Record<string, ReadingMode>>({})
const loading = ref(false)
const detectedMonth = ref<string>('')

// 从后端API提取月份
const extractMonthFromFilename = async (filename: string): Promise<string> => {
  if (!filename) return ''
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/import/extract-month-from-filename`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ filename })
    })
    
    const result = await response.json()
    
    if (result.success) {
      return result.detected_month || ''
    } else {
      console.error('提取月份信息失败:', result.message)
      return ''
    }
  } catch (error) {
    console.error('调用月份提取API失败:', error)
    return ''
  }
}

// 生成月份选项
const monthOptions = computed(() => {
  const options = []
  const currentDate = new Date()
  
  // 生成最近12个月的选项
  for (let i = 0; i < 12; i++) {
    const date = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const value = `${year}-${month}`
    const label = `${year}年${month}月`
    options.push({ value, label })
  }
  
  return options
})

const canConfirm = computed(() => {
  if (selectedMode.value === 'incremental') {
    return selectedMonth.value !== ''
  }
  return true
})

const trackingColumns = [
  {
    title: '门店名称',
    dataIndex: 'store_name',
    key: 'store_name',
  },
  {
    title: '月份',
    dataIndex: 'database_month',
    key: 'database_month',
  },
  {
    title: '最新日期',
    dataIndex: 'latest_date',
    key: 'latest_date',
  },
  {
    title: '记录数',
    dataIndex: 'total_records',
    key: 'total_records',
  },
  {
    title: '更新时间',
    dataIndex: 'updated_at',
    key: 'updated_at',
  },
]

// 加载读取模式建议
const loadReadingModeSuggestions = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/import/reading-mode-suggestions`)
    const result = await response.json()
    
    if (result.success) {
      readingModes.value = result.suggestions
    }
  } catch (error) {
    console.error('加载读取模式建议失败:', error)
  }
}

// 加载门店跟踪数据
const loadTrackingData = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/import/store-tracking`)
    const result = await response.json()
    
    if (result.success) {
      trackingData.value = result.tracking_data
    }
  } catch (error) {
    console.error('加载门店跟踪数据失败:', error)
  }
}

const selectMode = (mode: string) => {
  selectedMode.value = mode
  if (mode === 'full') {
    selectedMonth.value = ''
  }
}

const handleCancel = () => {
  emit('update:visible', false)
}

const handleConfirm = async () => {
  try {
    loading.value = true
    const config = {
      mode: selectedMode.value
    }
    emit('confirm', config)
    emit('update:visible', false)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadReadingModeSuggestions()
  await loadTrackingData()
  
  // 从文件名提取月份
  if (props.excelFilename) {
    detectedMonth.value = await extractMonthFromFilename(props.excelFilename)
    if (detectedMonth.value) {
      selectedMonth.value = detectedMonth.value
    }
  }
  
  // 如果没有检测到月份，默认选择当前月份
  if (!selectedMonth.value && monthOptions.value.length > 0) {
    selectedMonth.value = monthOptions.value[0].value
  }
})
</script>

<style scoped>
.reading-mode-selector {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  margin-bottom: 24px;
  text-align: center;
}

.header h3 {
  margin-bottom: 8px;
  color: #333;
}

.description {
  color: #666;
  font-size: 14px;
}

.mode-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.mode-card {
  border: 2px solid #e8e8e8;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.mode-card:hover {
  border-color: #1890ff;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.15);
}

.mode-card.selected {
  border-color: #1890ff;
  background: #f6ffed;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.2);
}

.mode-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.mode-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mode-title h4 {
  margin: 0;
  color: #333;
}

.mode-radio {
  margin: 0;
}

.mode-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.mode-badge.incremental {
  background: #52c41a;
  color: white;
}

.mode-badge.full {
  background: #1890ff;
  color: white;
}

.mode-description {
  color: #666;
  margin-bottom: 16px;
  line-height: 1.5;
}

.mode-advantages,
.mode-recommended {
  margin-bottom: 12px;
}

.mode-advantages h5,
.mode-recommended h5 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 14px;
}

.mode-advantages ul,
.mode-recommended ul {
  margin: 0;
  padding-left: 16px;
}

.mode-advantages li,
.mode-recommended li {
  color: #666;
  font-size: 13px;
  line-height: 1.4;
  margin-bottom: 4px;
}

.month-selector {
  margin-bottom: 24px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 6px;
}

.month-selector h4 {
  margin: 0 0 8px 0;
  color: #333;
}

.help-text {
  color: #666;
  font-size: 13px;
  margin-bottom: 12px;
}

.tracking-info {
  margin-bottom: 24px;
  padding: 16px;
  background: #f0f9ff;
  border-radius: 6px;
  border: 1px solid #bae7ff;
}

.tracking-info h4 {
  margin: 0 0 12px 0;
  color: #333;
}

.tracking-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.tracking-summary p {
  margin: 0;
  color: #666;
}

.tracking-details {
  margin-top: 12px;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #e8e8e8;
}

@media (max-width: 768px) {
  .mode-options {
    grid-template-columns: 1fr;
  }
}
</style>
