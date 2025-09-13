<template>
  <a-modal
    v-model:open="visible"
    title="选择Excel文件"
    :width="800"
    @ok="handleConfirm"
    @cancel="handleCancel"
    :confirm-loading="loading"
    ok-text="选择此文件"
    cancel-text="取消"
    :z-index="900"
    :mask-closable="false"
  >
    <div class="excel-file-selector">

      <!-- 文件列表 -->
      <div v-if="files.length > 0" class="file-list">
        <div class="file-list-header">
          <h4>发现 {{ files.length }} 个Excel文件</h4>
          <p class="tip-text">请选择要处理的Excel文件：</p>
        </div>
        
        <div class="file-items">
          <div
            v-for="(file, index) in files"
            :key="index"
            class="file-item"
            :class="{ 'selected': selectedFile?.path === file.path }"
            @click="selectFile(file)"
          >
            <div class="file-icon">
              <FileExcelOutlined :style="{ fontSize: '24px', color: '#52c41a' }" />
            </div>
            <div class="file-info">
              <div class="file-name">{{ file.name }}</div>
              <div class="file-details">
                <span class="file-size">{{ file.size_mb }} MB</span>
                <span class="file-time">{{ formatTime(file.modified_time) }}</span>
              </div>
            </div>
            <div class="file-status">
              <a-tag v-if="selectedFile?.path === file.path" color="blue">已选择</a-tag>
              <a-tag v-else color="default">点击选择</a-tag>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 无文件提示 -->
      <div v-else class="no-files">
        <div class="no-files-icon">
          <FileExcelOutlined :style="{ fontSize: '48px', color: '#d9d9d9' }" />
        </div>
        <h4>未找到Excel文件</h4>
        <p>请将Excel文件放入 <code>import/</code> 文件夹中</p>
        <div class="folder-path">
          <strong>文件夹路径：</strong>
          <code>{{ importFolderPath }}</code>
        </div>
      </div>
      
      <!-- 格式要求提示 -->
      <div class="format-requirements" style="margin-top: 20px; padding: 16px; background: #f6ffed; border: 1px solid #b7eb8f; border-radius: 6px;">
        <div style="display: flex; align-items: flex-start; gap: 12px;">
          <InfoCircleOutlined :style="{ fontSize: '16px', color: '#52c41a', marginTop: '2px' }" />
          <div>
            <h4 style="margin: 0 0 8px 0; color: #52c41a; font-size: 14px;">📋 Excel文件格式要求</h4>
            <ul style="margin: 0; padding-left: 16px; color: #666; font-size: 13px; line-height: 1.6;">
              <li>每个工作表代表一个门店，工作表名称需<strong>包含"店"字</strong></li>
              <li>数据按日期分组，<strong>每5列代表一天的数据，每一天后空1列</strong></li>
              <li><strong>包含在字段配置中选择的字段</strong>，即指标名称</li>
              <li><strong>支持.xlsx和.xls格式</strong></li>
              <li><strong>文件名建议包含月份信息</strong>，用于自动识别数据月份</li>
            </ul>
            
            <div style="margin-top: 12px; padding: 12px; background: #fff7e6; border: 1px solid #ffd591; border-radius: 4px;">
              <h5 style="margin: 0 0 8px 0; color: #d46b08; font-size: 13px;">📅 月份格式示例（推荐使用数字）：</h5>
              <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; font-size: 11px; color: #8c4a00;">
                <div>✅ <code>日激励（8月）.xlsx</code></div>
                <div>✅ <code>ksx_2025-09-08.xlsx</code></div>
                <div>✅ <code>data_202509.xlsx</code></div>
                <div>✅ <code>2025年9月数据.xlsx</code></div>
                <div>❌ <code>日激励（八月）.xlsx</code></div>
                <div>❌ <code>test_file.xlsx</code></div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-overlay">
        <div class="loading-content">
          <a-spin size="large" />
          <p>正在验证Excel文件是否合规...</p>
        </div>
      </div>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { message } from 'ant-design-vue'
import { FileExcelOutlined } from '@ant-design/icons-vue'
import dayjs from 'dayjs'

interface ExcelFile {
  name: string
  path: string
  size: number
  size_mb: number
  modified_time: number
  extension: string
}

interface Props {
  open: boolean
  importFolderPath?: string
}

interface Emits {
  (e: 'update:open', value: boolean): void
  (e: 'select', file: ExcelFile): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  importFolderPath: 'import/'
})

const emit = defineEmits<Emits>()

// 响应式数据
const visible = computed({
  get: () => props.open,
  set: (value) => emit('update:open', value)
})

const files = ref<ExcelFile[]>([])
const selectedFile = ref<ExcelFile | null>(null)
const loading = ref(false)

// 监听模态框打开，自动扫描文件
watch(visible, (newVisible) => {
  if (newVisible) {
    scanExcelFiles()
  } else {
    // 关闭时重置状态
    files.value = []
    selectedFile.value = null
  }
})

// 扫描Excel文件
const scanExcelFiles = async () => {
  try {
    loading.value = true
    const response = await fetch(`${API_BASE_URL}/api/import/excel-files`)
    const result = await response.json()
    
    if (result.success) {
      files.value = result.files
      
      // 如果有自动选择的文件，默认选中
      if (result.selected_file && result.files.length > 0) {
        const autoSelected = result.files.find((f: any) => f.path === result.selected_file)
        if (autoSelected) {
          selectedFile.value = autoSelected
        }
      }
      
      if (result.files.length === 0) {
        message.warning('未找到Excel文件，请将Excel文件放入import文件夹')
      } else if (result.files.length === 1) {
        message.info(`发现1个Excel文件，已自动选择: ${result.files[0].name}`)
      } else {
        message.info(`发现${result.files.length}个Excel文件，请选择要处理的文件`)
      }
    } else {
      message.error(result.message || '扫描Excel文件失败')
      files.value = []
    }
  } catch (error) {
    console.error('扫描Excel文件失败:', error)
    message.error('扫描Excel文件失败')
    files.value = []
  } finally {
    loading.value = false
  }
}

// 选择文件
const selectFile = (file: ExcelFile) => {
  selectedFile.value = file
}

// 格式化时间
const formatTime = (timestamp: number) => {
  return dayjs(timestamp * 1000).format('YYYY-MM-DD HH:mm:ss')
}

// 确认选择
const handleConfirm = async () => {
  if (!selectedFile.value) {
    message.error('请选择一个Excel文件')
    return
  }
  
  try {
    loading.value = true
    
    // 验证文件
    const response = await fetch(`${API_BASE_URL}/api/import/validate-excel`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        file_path: selectedFile.value.path
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      message.success(`已选择文件: ${selectedFile.value.name}`)
      emit('select', selectedFile.value)
      visible.value = false
    } else {
      message.error(`文件验证失败: ${result.message}`)
    }
  } catch (error) {
    console.error('验证文件失败:', error)
    message.error('验证文件失败')
  } finally {
    loading.value = false
  }
}

// 取消选择
const handleCancel = () => {
  emit('cancel')
  visible.value = false
}

// 定义API_BASE_URL
const API_BASE_URL = "http://localhost:18888"
</script>

<style scoped>
.excel-file-selector {
  min-height: 300px;
  position: relative;
}

.file-list-header {
  margin-bottom: 16px;
}

.file-list-header h4 {
  margin: 0 0 8px 0;
  color: #1890ff;
}

.tip-text {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.file-items {
  max-height: 400px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.file-item:hover {
  border-color: #1890ff;
  background-color: #f6ffed;
}

.file-item.selected {
  border-color: #1890ff;
  background-color: #e6f7ff;
}

.file-icon {
  margin-right: 12px;
}

.file-info {
  flex: 1;
}

.file-name {
  font-weight: 500;
  color: #262626;
  margin-bottom: 4px;
}

.file-details {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #8c8c8c;
}

.file-status {
  margin-left: 12px;
}

.no-files {
  text-align: center;
  padding: 40px 20px;
}

.no-files-icon {
  margin-bottom: 16px;
}

.no-files h4 {
  margin: 0 0 8px 0;
  color: #8c8c8c;
}

.no-files p {
  margin: 0 0 16px 0;
  color: #8c8c8c;
}

.folder-path {
  padding: 12px;
  background-color: #f5f5f5;
  border-radius: 4px;
  font-size: 12px;
}

.folder-path code {
  background-color: #fff;
  padding: 2px 6px;
  border-radius: 3px;
  color: #d46b08;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-content {
  text-align: center;
  padding: 40px 20px;
}

.loading-content p {
  margin-top: 16px;
  color: #666;
  font-size: 14px;
}
</style>
