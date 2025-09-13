<template>
  <a-modal
    :open="visible"
    @update:open="(value: boolean) => emit('update:visible', value)"
    title="选择数据月份"
    :width="600"
    @ok="handleConfirm"
    @cancel="handleCancel"
    :confirm-loading="loading"
    :ok-button-props="{ disabled: !canConfirm }"
    ok-text="确认选择"
    cancel-text="取消"
    :z-index="2500"
    :mask-closable="false"
  >
    <div class="month-selector">
      <div class="header">
        <h3>选择数据月份</h3>
        <p class="description">请确认或修改Excel数据对应的年份和月份</p>
        
        <!-- 显示检测到的月份 -->
        <div v-if="detectedMonth" class="detected-month-info" style="margin-top: 16px; padding: 12px; background: #e6f7ff; border: 1px solid #91d5ff; border-radius: 6px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="color: #1890ff; font-weight: 500;">📅 检测到月份：</span>
            <a-tag color="blue" style="font-size: 14px; font-weight: 500;">{{ detectedMonth }}</a-tag>
            <span style="color: #666; font-size: 13px;">（从文件名自动识别）</span>
          </div>
        </div>
        
        <div v-else class="no-month-warning" style="margin-top: 16px; padding: 12px; background: #fff7e6; border: 1px solid #ffd591; border-radius: 6px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="color: #d46b08;">⚠️ 未检测到月份信息</span>
            <span style="color: #666; font-size: 13px;">请手动选择数据对应的年份和月份</span>
          </div>
        </div>
      </div>

      <div class="month-selection">
        <div class="selection-row">
          <div class="selection-item">
            <label class="selection-label">年份：</label>
            <a-select
              v-model:value="selectedYear"
              style="width: 120px"
              placeholder="选择年份"
              :dropdown-style="{ zIndex: 2501 }"
            >
              <a-select-option v-for="year in yearOptions" :key="year" :value="year">
                {{ year }}年
              </a-select-option>
            </a-select>
          </div>
          
          <div class="selection-item">
            <label class="selection-label">月份：</label>
            <a-select
              v-model:value="selectedMonth"
              style="width: 120px"
              placeholder="选择月份"
              :dropdown-style="{ zIndex: 2501 }"
            >
              <a-select-option v-for="month in monthOptions" :key="month" :value="month">
                {{ month }}月
              </a-select-option>
            </a-select>
          </div>
        </div>
        
        <div class="selected-result" style="margin-top: 20px; padding: 16px; background: #f6ffed; border: 1px solid #b7eb8f; border-radius: 6px;">
          <div style="display: flex; align-items: center; gap: 12px;">
            <span style="color: #52c41a; font-weight: 500;">📅 选择结果：</span>
            <a-tag v-if="selectedYear && selectedMonth" color="green" style="font-size: 16px; font-weight: 500;">
              {{ selectedYear }}-{{ selectedMonth.toString().padStart(2, '0') }}
            </a-tag>
            <span v-else style="color: #999;">请选择年份和月份</span>
          </div>
        </div>
      </div>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'

// 移除未使用的API配置

interface Props {
  visible: boolean
  detectedMonth?: string
  excelFilename?: string
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'confirm', month: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const loading = ref(false)
const selectedYear = ref<number | null>(null)
const selectedMonth = ref<number | null>(null)

// 生成年份选项（当前年份前后各5年）
const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let i = currentYear - 5; i <= currentYear + 1; i++) {
    years.push(i)
  }
  return years
})

// 生成月份选项
const monthOptions = computed(() => {
  return Array.from({ length: 12 }, (_, i) => i + 1)
})

// 是否可以确认
const canConfirm = computed(() => {
  return selectedYear.value !== null && selectedMonth.value !== null
})

// 只在初始化时设置检测到的月份，不监听后续变化
const isInitialized = ref(false)

// 监听detectedMonth的变化，确保能正确设置初始值
watch(() => props.detectedMonth, (newMonth) => {
  console.log('MonthSelector: detectedMonth changed to:', newMonth, 'isInitialized:', isInitialized.value, 'current year:', selectedYear.value, 'current month:', selectedMonth.value)
  if (newMonth) {
    const [year, month] = newMonth.split('-')
    const newYear = parseInt(year)
    const newMonthNum = parseInt(month)
    
    // 如果还没有初始化，或者当前值与检测到的值不同，则更新
    if (!isInitialized.value || selectedYear.value !== newYear || selectedMonth.value !== newMonthNum) {
      selectedYear.value = newYear
      selectedMonth.value = newMonthNum
      isInitialized.value = true
      console.log('MonthSelector: set values - year:', selectedYear.value, 'month:', selectedMonth.value)
    }
  }
}, { immediate: true })

// 监听用户的选择变化，确保用户选择优先级最高
watch([selectedYear, selectedMonth], () => {
  // 用户手动选择后，标记为已初始化，避免被自动检测覆盖
  if (selectedYear.value && selectedMonth.value) {
    isInitialized.value = true
  }
})

// 移除文件名解析逻辑，只使用传入的detectedMonth

onMounted(() => {
  // 如果没有传入detectedMonth，使用当前年月作为默认值
  if (!props.detectedMonth && !isInitialized.value) {
    const now = new Date()
    selectedYear.value = now.getFullYear()
    selectedMonth.value = now.getMonth() + 1
    isInitialized.value = true
  }
})

const handleConfirm = async () => {
  if (!canConfirm.value) return
  
  try {
    loading.value = true
    
    const month = `${selectedYear.value}-${selectedMonth.value!.toString().padStart(2, '0')}`
    emit('confirm', month)
    emit('update:visible', false)
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  emit('update:visible', false)
}
</script>

<style scoped>
.month-selector {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  margin-bottom: 24px;
  text-align: center;
}

.header h3 {
  margin: 0 0 8px 0;
  color: #262626;
  font-size: 18px;
  font-weight: 600;
}

.description {
  margin: 0;
  color: #8c8c8c;
  font-size: 14px;
  line-height: 1.5;
}

.month-selection {
  margin-top: 24px;
}

.selection-row {
  display: flex;
  gap: 24px;
  justify-content: center;
  align-items: center;
}

.selection-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.selection-label {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
}

.selected-result {
  text-align: center;
}

/* 确保下拉框正确显示 */
:deep(.ant-select-dropdown) {
  z-index: 2501 !important;
}

:deep(.ant-select-item) {
  z-index: 2501 !important;
}

</style>
