<template>
  <div class="action-bar">
    <div class="data-info">
      共 <a-tag color="blue">{{ total }}</a-tag> 条数据
    </div>
    <a-space>
      <a-button 
        type="primary" 
        :loading="syncLoading"
        @click="$emit('sync')"
      >
        <template #icon>
          <SyncOutlined />
        </template>
        同步数据
      </a-button>
      <a-button 
        type="default"
        @click="$emit('config')"
      >
        <template #icon>
          <SettingOutlined />
        </template>
        门店配置
      </a-button>
      <a-button 
        type="default"
        @click="$emit('fieldConfig')"
      >
        <template #icon>
          <FieldTimeOutlined />
        </template>
        字段配置
      </a-button>
      <!-- CSV导出按钮已隐藏 -->
      <a-button 
        type="default" 
        :disabled="!hasData"
        @click="$emit('exportExcel')"
      >
        <template #icon>
          <FileExcelOutlined />
        </template>
        导出Excel
      </a-button>
    </a-space>
  </div>
</template>

<script setup lang="ts">
import { SyncOutlined, SettingOutlined, DownloadOutlined, FileExcelOutlined, FieldTimeOutlined } from '@ant-design/icons-vue'

interface Props {
  total: number
  syncLoading: boolean
  hasData: boolean
}

interface Emits {
  (e: 'sync'): void
  (e: 'config'): void
  (e: 'fieldConfig'): void
  (e: 'export'): void
  (e: 'exportExcel'): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>

<style scoped>
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.data-info {
  font-size: 14px;
  color: #666;
}

@media (max-width: 768px) {
  .action-bar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .action-bar {
    padding: 12px;
  }
}
</style>
