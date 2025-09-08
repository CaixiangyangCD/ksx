<template>
  <Modal
    v-model:open="visible"
    width="90vw"
    :footer="null"
    centered
    @cancel="handleCancel"
    class="store-config-modal-fullscreen"
  >
    <template #title>
      <div class="modal-title">
        <span>门店配置</span>
        <a-tooltip title="配置Excel导出时需要包含的门店数据。选择门店后，导出的Excel文件将只包含这些门店的数据，未选择的门店将被过滤掉。">
          <QuestionCircleOutlined class="help-icon" />
        </a-tooltip>
      </div>
    </template>
    <div class="store-config-modal">
      <div class="config-layout">
        <!-- 左侧：门店选择区域 -->
        <div class="left-panel">
          <div class="config-section">
            <h4>选择需要导出的门店</h4>
            
            <!-- 搜索框 -->
            <div class="search-section">
              <a-input
                v-model:value="searchKeyword"
                placeholder="搜索门店名称..."
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
                  <a-button size="small" @click="selectFiltered" v-if="filteredStores.length > 0">
                    选择搜索结果 ({{ filteredStores.length }})
                  </a-button>
                </a-space>
              </div>
            </div>
            
            <div class="store-list">
              <div class="store-grid">
                <a-checkbox 
                  v-for="store in filteredStores" 
                  :key="store.id" 
                  :checked="selectedStores.includes(store.id)"
                  @change="(e: any) => handleStoreChange(store.id, e.target.checked)"
                  class="store-item"
                >
                  {{ store.store_name }}
                </a-checkbox>
              </div>
              <div v-if="stores.length === 0" class="no-stores">
                <p>暂无门店数据，请先同步数据</p>
              </div>
              <div v-else-if="filteredStores.length === 0" class="no-results">
                <p>没有找到匹配的门店</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：已选择门店展示区域 -->
        <div class="right-panel">
          <div class="config-section">
            <h4>已选择门店</h4>
            <div class="selection-header">
              <p>已选中 <a-tag color="blue">{{ selectedStores.length }}</a-tag> 个门店</p>
              <a-button size="small" type="link" @click="clearAll" v-if="selectedStores.length > 0">清空所有</a-button>
            </div>
            
            <div class="selected-stores-detail" v-if="selectedStores.length > 0">
              <div class="selected-stores-list">
                <a-tooltip 
                  v-for="storeId in selectedStores" 
                  :key="storeId"
                  :title="getStoreName(storeId)"
                  placement="top"
                >
                  <div class="store-tag-wrapper">
                    <a-tag 
                      color="green"
                      class="store-tag"
                    >
                      {{ getStoreName(storeId) }}
                    </a-tag>
                    <span 
                      class="custom-close-btn"
                      @click="removeStore(storeId)"
                      title="删除"
                    >
                      ×
                    </span>
                  </div>
                </a-tooltip>
              </div>
            </div>
            <div v-else class="no-selection">
              <p>暂未选择任何门店</p>
            </div>
          </div>

          <!-- 显示已保存的配置信息 -->
          <div class="config-section" v-if="currentRule && currentRule.selected_stores.length > 0">
            <h4>已保存配置</h4>
            <div class="saved-rule">
              <div class="rule-header">
                <p>已保存 <a-tag color="orange">{{ currentRule.selected_stores.length }}</a-tag> 个门店</p>
                <p class="rule-time">保存时间: {{ currentRule.updated_at }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-actions">
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
import { ref, watch, computed } from 'vue'
import { Modal, message } from 'ant-design-vue'
import { SearchOutlined, QuestionCircleOutlined } from '@ant-design/icons-vue'

interface Store {
  id: number
  store_name: string
  created_at: string
  updated_at: string
}

interface ExportRule {
  id: number
  rule_name: string
  selected_stores: number[]
  is_default: boolean
  created_at: string
  updated_at: string
}

interface Props {
  open: boolean
  stores: Store[]
  currentRule: ExportRule | null
}

interface Emits {
  (e: 'update:open', value: boolean): void
  (e: 'save', selectedStores: number[]): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visible = ref(false)
const selectedStores = ref<number[]>([])
const saving = ref(false)
const searchKeyword = ref('')
const debouncedSearchKeyword = ref('')

// 创建防抖搜索函数
let searchTimeout: number | null = null
const debouncedSearch = (keyword: string) => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    debouncedSearchKeyword.value = keyword
  }, 300)
}

// 监听搜索关键词变化
watch(searchKeyword, (newKeyword) => {
  debouncedSearch(newKeyword)
})

// 过滤后的门店列表
const filteredStores = computed(() => {
  if (!debouncedSearchKeyword.value.trim()) {
    return props.stores
  }
  
  const keyword = debouncedSearchKeyword.value.toLowerCase().trim()
  return props.stores.filter(store => 
    store.store_name.toLowerCase().includes(keyword)
  )
})

// 监听props变化
watch(() => props.open, (newVal) => {
  visible.value = newVal
  if (newVal) {
    // 初始化时，如果有已保存的配置，则同步到选择列表
    if (props.currentRule && props.currentRule.selected_stores) {
      selectedStores.value = [...props.currentRule.selected_stores]
    } else {
      selectedStores.value = []
    }
    // 清空搜索关键词
    searchKeyword.value = ''
    debouncedSearchKeyword.value = ''
  }
})

watch(visible, (newVal) => {
  emit('update:open', newVal)
})

const handleCancel = () => {
  visible.value = false
}

const handleSave = async () => {
  if (selectedStores.value.length === 0) {
    message.warning('请至少选择一个门店')
    return
  }

  saving.value = true
  try {
    emit('save', selectedStores.value)
  } finally {
    saving.value = false
  }
}

// 快速操作功能
const selectAll = () => {
  selectedStores.value = props.stores.map(store => store.id)
  message.success(`已选择全部 ${props.stores.length} 个门店`)
}

const clearAll = () => {
  selectedStores.value = []
  message.info('已清空所有选择')
}

const selectFiltered = () => {
  const filteredIds = filteredStores.value.map(store => store.id)
  // 合并当前选择和搜索结果，去重
  const newSelection = [...new Set([...selectedStores.value, ...filteredIds])]
  selectedStores.value = newSelection
  message.success(`已选择搜索结果中的 ${filteredIds.length} 个门店`)
}

// 获取门店名称
const getStoreName = (storeId: number) => {
  const store = props.stores.find(s => s.id === storeId)
  return store ? store.store_name : `门店ID: ${storeId}`
}

// 处理门店选择变化
const handleStoreChange = (storeId: number, checked: boolean) => {
  if (checked) {
    // 添加到选择列表
    if (!selectedStores.value.includes(storeId)) {
      selectedStores.value.push(storeId)
    }
  } else {
    // 从选择列表移除
    const index = selectedStores.value.indexOf(storeId)
    if (index > -1) {
      selectedStores.value.splice(index, 1)
    }
  }
}

// 移除门店
const removeStore = (storeId: number) => {
  const index = selectedStores.value.indexOf(storeId)
  if (index > -1) {
    selectedStores.value.splice(index, 1)
    message.info(`已移除门店: ${getStoreName(storeId)}`)
  }
}
</script>

<style scoped>
:deep(.store-config-modal-fullscreen .ant-modal-body) {
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

.store-config-modal {
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
  
  .store-list {
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
  
  .no-stores, .no-results {
    text-align: center;
    padding: 20px;
    color: #999;
  }
  
  .no-results {
    color: #ff7875;
  }
  
  .selection-info {
    margin-top: 12px;
    padding: 8px 12px;
    background-color: #f6ffed;
    border: 1px solid #b7eb8f;
    border-radius: 6px;
    
    p {
      margin: 0;
      font-size: 14px;
    }
  }
  
  .store-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 8px;
    align-items: start;
  }
  
  .store-item {
    margin: 0;
    padding: 12px 16px;
    border-radius: 6px;
    transition: all 0.2s;
    border: 1px solid #f0f0f0;
    background-color: #fafafa;
    display: flex;
    align-items: center;
    min-height: 44px;
    
    &:hover {
      background-color: #f5f5f5;
      border-color: #d9d9d9;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    :deep(.ant-checkbox) {
      margin-right: 12px;
      flex-shrink: 0;
    }
    
    :deep(.ant-checkbox + span) {
      flex: 1;
      line-height: 1.4;
      word-break: break-word;
    }
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
  
  .selected-stores-detail {
    flex: 1;
    overflow-y: auto;
    
    .selected-stores-list {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      
      .store-tag-wrapper {
        position: relative;
        display: inline-block;
        margin: 0;
        
        .store-tag {
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
  }
}
</style>
