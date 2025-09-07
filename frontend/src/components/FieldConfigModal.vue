<template>
  <Modal
    v-model:open="visible"
    width="90vw"
    :footer="null"
    centered
    @cancel="handleCancel"
    class="field-config-modal-fullscreen"
  >
    <template #title>
      <div class="modal-title">
        <span>字段配置</span>
        <a-tooltip title="配置Excel导出时需要包含的数据字段。选择字段后，导出的Excel文件将只包含这些字段的数据，未选择的字段将被过滤掉。修改字段配置会创建新的Excel文件。">
          <QuestionCircleOutlined class="help-icon" />
        </a-tooltip>
      </div>
    </template>
    <div class="field-config-modal">
      <div class="config-layout">
        <!-- 左侧：字段选择区域 -->
        <div class="left-panel">
          <div class="config-section">
            <h4>选择需要导出的字段</h4>
            
            <!-- 搜索框 -->
            <div class="search-section">
              <a-input
                v-model:value="searchKeyword"
                placeholder="搜索字段名称..."
                allow-clear
                style="margin-bottom: 12px"
              >
                <template #prefix>
                  <SearchOutlined />
                </template>
              </a-input>
              
              <!-- 快速操作按钮 -->
              <div class="quick-actions">
                <a-space>
                  <a-button size="small" @click="selectAll">全选</a-button>
                  <a-button size="small" @click="clearAll">清空</a-button>
                  <a-button size="small" @click="selectFiltered" v-if="filteredFields.length > 0">
                    选择搜索结果 ({{ filteredFields.length }})
                  </a-button>
                </a-space>
              </div>
            </div>
            
            <div class="field-list">
              <a-checkbox-group v-model:value="selectedFields" class="checkbox-group">
                <div class="field-grid">
                  <a-checkbox 
                    v-for="field in filteredFields" 
                    :key="field.key" 
                    :value="field.key"
                    class="field-item"
                  >
                    {{ field.name }}
                  </a-checkbox>
                </div>
              </a-checkbox-group>
              <div v-if="Object.keys(fieldConfig).length === 0" class="no-fields">
                <p>暂无字段数据</p>
              </div>
              <div v-else-if="filteredFields.length === 0" class="no-results">
                <p>没有找到匹配的字段</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：已选择字段展示区域 -->
        <div class="right-panel">
          <div class="config-section">
            <h4>已选择字段</h4>
            <div class="selection-header">
              <p>已选中 <a-tag color="blue">{{ selectedFields.length }}</a-tag> 个字段</p>
              <a-button size="small" type="link" @click="clearAll" v-if="selectedFields.length > 0">清空所有</a-button>
            </div>
            
            <div class="selected-fields-detail" v-if="selectedFields.length > 0">
              <div class="selected-fields-list">
                <a-tooltip 
                  v-for="fieldKey in selectedFields" 
                  :key="fieldKey"
                  :title="getFieldName(fieldKey)"
                  placement="top"
                >
                  <div class="field-tag-wrapper">
                    <a-tag 
                      color="green"
                      class="field-tag"
                    >
                      {{ getFieldName(fieldKey) }}
                    </a-tag>
                    <span 
                      class="custom-close-btn"
                      @click="removeField(fieldKey)"
                      title="删除"
                    >
                      ×
                    </span>
                  </div>
                </a-tooltip>
              </div>
            </div>
            <div v-else class="no-selection">
              <p>暂未选择任何字段</p>
            </div>
          </div>

          <!-- 显示已保存的配置信息 -->
          <div class="config-section" v-if="currentRule && currentRule.selected_fields.length > 0">
            <h4>已保存配置</h4>
            <div class="saved-rule">
              <div class="rule-header">
                <p>已保存 <a-tag color="orange">{{ currentRule.selected_fields.length }}</a-tag> 个字段</p>
                <p class="rule-time">保存时间: {{ currentRule.updated_at }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-actions">
        <div class="warning-alert" v-if="hasConfigChanged">
          <a-alert
            message="配置已修改"
            description="修改字段配置后，Excel导出将创建新文件"
            type="warning"
            show-icon
            :closable="false"
            size="small"
          />
        </div>
        <a-space>
          <a-button @click="handleCancel">
            取消
          </a-button>
          <a-button type="primary" @click="handleSave" :loading="saving">
            保存配置
          </a-button>
        </a-space>
      </div>
    </div>
  </Modal>
</template>

<script setup lang="ts">
import { ref, watch, computed, h } from 'vue'
import { Modal, message } from 'ant-design-vue'
import { SearchOutlined, ExclamationCircleOutlined, QuestionCircleOutlined } from '@ant-design/icons-vue'

interface FieldConfig {
  name: string
  comment: string
}

interface Props {
  open: boolean
  fieldConfig: Record<string, FieldConfig>
  currentRule: any
}

interface Emits {
  (e: 'update:open', value: boolean): void
  (e: 'save', selectedFields: string[]): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visible = ref(false)
const selectedFields = ref<string[]>([])
const saving = ref(false)
const searchKeyword = ref('')
const originalFields = ref<string[]>([]) // 保存原始配置

// 过滤后的字段列表
const filteredFields = computed(() => {
  if (!searchKeyword.value.trim()) {
    return Object.entries(props.fieldConfig).map(([key, config]) => ({
      key,
      name: config.name
    }))
  }
  
  const keyword = searchKeyword.value.toLowerCase().trim()
  return Object.entries(props.fieldConfig)
    .filter(([key, config]) => 
      config.name.toLowerCase().includes(keyword) || 
      key.toLowerCase().includes(keyword)
    )
    .map(([key, config]) => ({
      key,
      name: config.name
    }))
})

// 检测配置是否发生变更
const hasConfigChanged = computed(() => {
  if (originalFields.value.length !== selectedFields.value.length) {
    return true
  }
  
  // 检查字段是否相同（忽略顺序）
  const originalSet = new Set(originalFields.value.sort())
  const currentSet = new Set(selectedFields.value.sort())
  
  if (originalSet.size !== currentSet.size) {
    return true
  }
  
  for (const field of originalSet) {
    if (!currentSet.has(field)) {
      return true
    }
  }
  
  return false
})

// 监听props变化
watch(() => props.open, (newVal) => {
  visible.value = newVal
  if (newVal) {
    // 初始化时，如果有已保存的配置，则同步到选择列表
    if (props.currentRule && props.currentRule.selected_fields) {
      selectedFields.value = [...props.currentRule.selected_fields]
      originalFields.value = [...props.currentRule.selected_fields] // 保存原始配置
    } else {
      selectedFields.value = []
      originalFields.value = []
    }
    // 清空搜索关键词
    searchKeyword.value = ''
  }
})

watch(visible, (newVal) => {
  emit('update:open', newVal)
})

const handleCancel = () => {
  visible.value = false
}

const handleSave = async () => {
  if (selectedFields.value.length === 0) {
    message.warning('请至少选择一个字段')
    return
  }

  // 如果配置发生变更，显示警告
  if (hasConfigChanged.value) {
    const confirmed = await new Promise((resolve) => {
      Modal.confirm({
        title: '配置变更确认',
        icon: h(ExclamationCircleOutlined),
        content: '您已修改字段配置，本次导出的Excel将会创建新文件，不会覆盖现有文件。是否确认保存？',
        okText: '确认保存',
        cancelText: '取消',
        onOk: () => resolve(true),
        onCancel: () => resolve(false)
      })
    })
    
    if (!confirmed) {
      return
    }
  }

  saving.value = true
  try {
    emit('save', selectedFields.value)
    // 保存成功后关闭Modal
    visible.value = false
  } finally {
    saving.value = false
  }
}

// 快速操作功能
const selectAll = () => {
  selectedFields.value = Object.keys(props.fieldConfig)
  message.success(`已选择全部 ${Object.keys(props.fieldConfig).length} 个字段`)
}

const clearAll = () => {
  selectedFields.value = []
  message.info('已清空所有选择')
}

const selectFiltered = () => {
  const filteredKeys = filteredFields.value.map(field => field.key)
  // 合并当前选择和搜索结果，去重
  const newSelection = [...new Set([...selectedFields.value, ...filteredKeys])]
  selectedFields.value = newSelection
  message.success(`已选择搜索结果中的 ${filteredKeys.length} 个字段`)
}

// 获取字段名称
const getFieldName = (fieldKey: string) => {
  const field = props.fieldConfig[fieldKey]
  return field ? field.name : `字段: ${fieldKey}`
}

// 移除字段
const removeField = (fieldKey: string) => {
  const index = selectedFields.value.indexOf(fieldKey)
  if (index > -1) {
    selectedFields.value.splice(index, 1)
    message.info(`已移除字段: ${getFieldName(fieldKey)}`)
  }
}
</script>

<style scoped>
:deep(.field-config-modal-fullscreen .ant-modal-body) {
  padding: 24px;
  max-height: 80vh;
  overflow: hidden;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .help-icon {
    color: #1890ff;
    cursor: help;
    font-size: 14px;
    
    &:hover {
      color: #40a9ff;
    }
  }
}

.field-config-modal {
  height: 70vh;
  display: flex;
  flex-direction: column;
  
  .config-layout {
    display: flex;
    gap: 24px;
    flex: 1;
    overflow: hidden;
    
    .left-panel {
      flex: 2;
      overflow: hidden;
    }
    
    .right-panel {
      flex: 1;
      overflow: hidden;
    }
  }
  
  .config-section {
    margin-bottom: 24px;
    height: 100%;
    display: flex;
    flex-direction: column;
    
    h4 {
      margin-bottom: 12px;
      color: #333;
      font-weight: 600;
    }
  }
  
  .search-section {
    margin-bottom: 16px;
    
    .quick-actions {
      margin-top: 8px;
    }
  }
  
  .field-list {
    flex: 1;
    overflow-y: auto;
    border: 1px solid #d9d9d9;
    border-radius: 6px;
    padding: 12px;
  }
  
  .checkbox-group {
    width: 100%;
    
    :deep(.ant-checkbox-group) {
      width: 100%;
      display: block;
    }
  }
  
  .field-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 8px;
  }
  
  .field-item {
    margin: 0;
    padding: 8px 12px;
    border-radius: 4px;
    transition: background-color 0.2s;
    border: 1px solid #f0f0f0;
    
    &:hover {
      background-color: #f5f5f5;
      border-color: #d9d9d9;
    }
  }
  
  .no-fields, .no-results {
    text-align: center;
    padding: 20px;
    color: #999;
  }
  
  .no-results {
    color: #ff7875;
  }
  
  .selection-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    
    p {
      margin: 0;
    }
  }
  
  .selected-fields-detail {
    flex: 1;
    overflow-y: auto;
    
    .selected-fields-list {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      
      .field-tag-wrapper {
        position: relative;
        display: inline-block;
        margin: 0;
        
        .field-tag {
          margin: 0;
          max-width: 180px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          padding-right: 20px;
        }
        
        .custom-close-btn {
          position: absolute;
          right: 4px;
          top: 50%;
          transform: translateY(-50%);
          z-index: 10;
          background: transparent;
          border-radius: 50%;
          width: 16px;
          height: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 12px;
          cursor: pointer;
          transition: all 0.2s ease;
          color: #999;
          font-weight: bold;
          line-height: 1;
          
          &:hover {
            background: #ff4d4f;
            color: white;
            transform: translateY(-50%) scale(1.1);
          }
        }
      }
    }
  }
  
  .no-selection {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
    font-style: italic;
  }
  
  .saved-rule {
    padding: 12px;
    background-color: #fff7e6;
    border-radius: 6px;
    border: 1px solid #ffd591;
    
    .rule-header {
      p {
        margin: 0 0 8px 0;
        
        &:last-child {
          margin-bottom: 0;
        }
      }
      
      .rule-time {
        color: #666;
        font-size: 12px;
      }
    }
  }
  
  .modal-actions {
    text-align: right;
    padding-top: 16px;
    border-top: 1px solid #f0f0f0;
    
    .warning-alert {
      margin-bottom: 12px;
      text-align: left;
    }
  }
}
</style>
