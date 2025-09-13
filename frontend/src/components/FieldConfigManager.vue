<template>
  <div class="field-config-manager">
    <div class="header">
      <h2>字段配置管理</h2>
      <p class="description">选择需要从Excel文件中提取的指标字段</p>
    </div>

    <div class="config-section">
      <div class="section-header">
        <h3>字段选择</h3>
        <div class="actions">
          <button @click="selectAll" class="btn btn-secondary">全选</button>
          <button @click="selectNone" class="btn btn-secondary">全不选</button>
          <button @click="resetToDefault" class="btn btn-secondary">重置为默认</button>
        </div>
      </div>

      <div class="field-groups">
        <div v-for="(group, groupName) in fieldGroups" :key="groupName" class="field-group">
          <h4 class="group-title">{{ groupName }}</h4>
          <div class="field-list">
            <label 
              v-for="field in group" 
              :key="field.key" 
              class="field-item"
            >
              <input 
                type="checkbox" 
                :value="field.key"
                v-model="selectedFields"
                class="field-checkbox"
              />
              <div class="field-info">
                <span class="field-name">{{ field.name }}</span>
                <span class="field-comment">{{ field.comment }}</span>
              </div>
            </label>
          </div>
        </div>
      </div>
    </div>

    <div class="selected-info">
      <p>已选择 {{ selectedFields.length }} 个字段</p>
    </div>

    <div class="actions">
      <button @click="saveConfig" class="btn btn-primary" :disabled="!hasChanges">
        保存配置
      </button>
      <button @click="cancelChanges" class="btn btn-secondary" :disabled="!hasChanges">
        取消更改
      </button>
    </div>

    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface FieldConfig {
  name: string
  comment: string
}

interface FieldGroups {
  [key: string]: Array<{ key: string; name: string; comment: string }>
}

const selectedFields = ref<string[]>([])
const originalFields = ref<string[]>([])
const fieldConfig = ref<Record<string, FieldConfig>>({})
const message = ref('')
const messageType = ref<'success' | 'error' | ''>('')

// 字段分组
const fieldGroups = computed<FieldGroups>(() => {
  const groups: FieldGroups = {
    '基础信息': [],
    '取消率相关': [],
    '评分相关': [],
    '库存相关': [],
    '其他指标': []
  }

  Object.entries(fieldConfig.value).forEach(([key, config]) => {
    const field = { key, ...config }
    
    if (key.includes('area') || key.includes('MDShow') || key.includes('createDateShow') || key.includes('totalScore')) {
      groups['基础信息'].push(field)
    } else if (key.includes('Cancel') || key.includes('Refund')) {
      groups['取消率相关'].push(field)
    } else if (key.includes('Rating') || key.includes('Score') || key.includes('Punctuality')) {
      groups['评分相关'].push(field)
    } else if (key.includes('Stock') || key.includes('Inventory') || key.includes('Warehouse')) {
      groups['库存相关'].push(field)
    } else {
      groups['其他指标'].push(field)
    }
  })

  return groups
})

const hasChanges = computed(() => {
  return JSON.stringify(selectedFields.value.sort()) !== JSON.stringify(originalFields.value.sort())
})

// 加载字段配置
const loadFieldConfig = async () => {
  try {
    const response = await fetch('/api/field-config')
    const result = await response.json()
    
    if (result.success) {
      fieldConfig.value = result.field_config
    } else {
      showMessage('加载字段配置失败: ' + result.message, 'error')
    }
  } catch (error) {
    showMessage('加载字段配置失败: ' + error, 'error')
  }
}

// 加载当前配置
const loadCurrentConfig = async () => {
  try {
    const response = await fetch('/api/export-field-rule')
    const result = await response.json()
    
    if (result.success && result.data) {
      selectedFields.value = result.data.selected_fields || []
      originalFields.value = [...selectedFields.value]
    } else {
      // 如果没有配置，默认选择所有字段
      selectedFields.value = Object.keys(fieldConfig.value)
      originalFields.value = [...selectedFields.value]
    }
  } catch (error) {
    showMessage('加载当前配置失败: ' + error, 'error')
  }
}

// 保存配置
const saveConfig = async () => {
  try {
    const response = await fetch('/api/export-field-rule', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        selected_fields: selectedFields.value
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      originalFields.value = [...selectedFields.value]
      showMessage('配置保存成功', 'success')
    } else {
      showMessage('保存配置失败: ' + result.message, 'error')
    }
  } catch (error) {
    showMessage('保存配置失败: ' + error, 'error')
  }
}

// 取消更改
const cancelChanges = () => {
  selectedFields.value = [...originalFields.value]
  showMessage('已取消更改', 'success')
}

// 全选
const selectAll = () => {
  selectedFields.value = Object.keys(fieldConfig.value)
}

// 全不选
const selectNone = () => {
  selectedFields.value = []
}

// 重置为默认
const resetToDefault = () => {
  // 选择一些常用的字段作为默认
  const defaultFields = [
    'area', 'MDShow', 'createDateShow', 'totalScore',
    'monthlyCanceledRate', 'dailyCanceledRate',
    'dailyMeituanRating', 'dailyElemeRating',
    'monthlyAvgStockRate', 'monthlyAvgTop500StockRate'
  ]
  selectedFields.value = defaultFields.filter(field => fieldConfig.value[field])
}

// 显示消息
const showMessage = (msg: string, type: 'success' | 'error' | '') => {
  message.value = msg
  messageType.value = type
  setTimeout(() => {
    message.value = ''
    messageType.value = ''
  }, 3000)
}

onMounted(async () => {
  await loadFieldConfig()
  await loadCurrentConfig()
})
</script>

<style scoped>
.field-config-manager {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  margin-bottom: 30px;
}

.header h2 {
  color: #333;
  margin-bottom: 10px;
}

.description {
  color: #666;
  font-size: 14px;
}

.config-section {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  color: #333;
}

.actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-primary:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #545b62;
}

.field-groups {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.field-group {
  background: white;
  border-radius: 6px;
  padding: 15px;
}

.group-title {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

.field-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.field-item:hover {
  background-color: #f0f0f0;
}

.field-checkbox {
  margin-top: 2px;
}

.field-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.field-name {
  font-weight: 500;
  color: #333;
}

.field-comment {
  font-size: 12px;
  color: #666;
}

.selected-info {
  margin-bottom: 20px;
  padding: 10px;
  background: #e7f3ff;
  border-radius: 4px;
  color: #0066cc;
}

.actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.message {
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
}

.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style>
