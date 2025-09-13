<template>
  <Modal
    v-model:open="visible"
    title="Excel导出"
    width="600px"
    :footer="null"
    centered
    @cancel="handleCancel"
    :mask-closable="false"
  >
    <div class="excel-export-modal">
      <div class="config-section">
        <h4>导出说明</h4>
        <div class="export-info">
          <a-alert
            message="Excel导出格式说明"
            type="info"
            show-icon
          >
            <template #description>
              <ul>
                <li>每月数据将生成一个独立的工作表</li>
                <li>每个门店占多行，每个指标占一行</li>
                <li>每天的数据将作为列显示</li>
                <li>门店名称将合并单元格显示</li>
                <li>使用已配置的字段和门店规则</li>
              </ul>
            </template>
          </a-alert>
        </div>
      </div>

      <div class="config-section">
        <h4>导出设置</h4>
        <div class="export-settings">
          <div class="date-range">
            <a-form-item label="选择日期">
              <a-date-picker 
                v-model:value="selectedDate"
                format="YYYY-MM-DD"
                placeholder="选择要导出的日期"
                style="width: 100%"
              />
            </a-form-item>
          </div>
        </div>
      </div>

      <div class="config-section">
        <h4>当前配置</h4>
        <div class="current-config">
          <div class="config-item">
            <span class="config-label">门店配置：</span>
            <a-tag color="blue">{{ currentStoreRule ? currentStoreRule.selected_stores.length : 0 }} 个门店</a-tag>
          </div>
          <div class="config-item">
            <span class="config-label">字段配置：</span>
            <a-tag color="green">{{ currentFieldRule ? currentFieldRule.selected_fields.length : 0 }} 个字段</a-tag>
          </div>
        </div>
      </div>

      <div class="modal-actions">
        <a-space>
          <a-button @click="handleCancel">
            取消
          </a-button>
          <a-button 
            type="primary" 
            @click="handleExport" 
            :loading="exporting"
          >
            开始导出
          </a-button>
        </a-space>
      </div>
    </div>
  </Modal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Modal, message } from 'ant-design-vue'
import dayjs from 'dayjs'

interface Props {
  open: boolean
  currentStoreRule: any
  currentFieldRule: any
  currentQueryDate?: string
}

interface Emits {
  (e: 'update:open', value: boolean): void
  (e: 'export', selectedDate: dayjs.Dayjs | null): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visible = ref(false)
const exporting = ref(false)
const selectedDate = ref<dayjs.Dayjs | null>(null)

// 监听props变化
watch(() => props.open, (newVal) => {
  visible.value = newVal
  // 当Modal打开时，设置默认日期为当前查询日期
  if (newVal && props.currentQueryDate) {
    selectedDate.value = dayjs(props.currentQueryDate)
  }
})

watch(visible, (newVal) => {
  emit('update:open', newVal)
})

const handleCancel = () => {
  visible.value = false
}

const handleExport = async () => {
  exporting.value = true
  try {
    emit('export', selectedDate.value)
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.excel-export-modal {
  .config-section {
    margin-bottom: 24px;
    
    h4 {
      margin-bottom: 12px;
      color: #333;
      font-weight: 600;
    }
  }
  
  .export-info {
    .ant-alert {
      ul {
        margin: 8px 0 0 0;
        padding-left: 20px;
        
        li {
          margin-bottom: 4px;
          color: #666;
        }
      }
    }
  }
  
  .current-config {
    .config-item {
      display: flex;
      align-items: center;
      margin-bottom: 12px;
      
      .config-label {
        margin-right: 8px;
        color: #666;
        min-width: 80px;
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
