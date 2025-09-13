<template>
  <a-modal
    v-model:open="visible"
    title="Excel数据预览"
    :width="1200"
    @cancel="handleCancel"
    :z-index="1000"
    :mask-closable="false"
  >
    <template #footer>
      <div class="custom-footer">
        <div class="footer-tip">
          提示：对比导出将Excel数据与系统数据进行对比分析，生成差异报告
        </div>
        <div class="footer-buttons">
          <a-button @click="handleCancel">取消</a-button>
          <a-button 
            type="primary" 
            @click="handleCompareExport"
            :loading="compareLoading"
          >
            对比导出
          </a-button>
        </div>
      </div>
    </template>
    <div class="excel-data-preview">
      <!-- 文件信息 -->
      <div class="file-info" style="margin-bottom: 16px; padding: 12px; background: #f6ffed; border: 1px solid #b7eb8f; border-radius: 6px;">
        <div style="display: flex; align-items: center; gap: 24px; color: #52c41a; font-size: 14px;">
          <span><strong>文件名：</strong>{{ fileInfo.name }}</span>
          <span><strong>文件大小：</strong>{{ fileInfo.size_mb }} MB</span>
          <span><strong>门店数量：</strong>{{ stores.length }} 个</span>
          <span v-if="detectedMonth"><strong>数据月份：</strong><a-tag color="blue">{{ detectedMonth }}</a-tag></span>
        </div>
      </div>

      <!-- 门店列表 -->
      <div class="stores-list" style="margin-bottom: 20px;">
        <a-table
          :columns="storeColumns"
          :data-source="storeTableData"
          :pagination="false"
          :scroll="{ x: 400 }"
          size="small"
          bordered
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'action'">
              <a-button type="link" size="small" @click="viewStoreDetails(record.name)">
                查看详情
              </a-button>
            </template>
          </template>
        </a-table>
      </div>


      <!-- 加载状态 -->
      <div v-if="props.loading" class="loading-overlay">
        <div class="loading-content">
          <a-spin size="large" />
          <p>正在分析Excel文件数据...</p>
        </div>
      </div>

    </div>

    <!-- 数据对比结果Modal -->
    <DataComparisonResultModal
      v-model:open="showComparisonResult"
      :errors="comparisonErrors"
      :warnings="comparisonWarnings"
      :comparison-data="comparisonData"
      :database-info="databaseInfo"
      @continue-export="handleContinueExport"
      @cancel="showComparisonResult = false"
    />
  </a-modal>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'
import DataComparisonResultModal from './DataComparisonResultModal.vue'

const API_BASE_URL = "http://localhost:18888"

interface ExcelFileInfo {
  name: string
  path: string
  size_mb: number
}

interface StoreInfo {
  name: string
  sheet_name: string
  total_rows: number
  total_columns: number
}

interface MetricData {
  metric_name: string
  yellow_line_exceeded: boolean | null
  data_value: any
  rectification_plan: string
  row_index: number
  column_index: number
}

interface Props {
  open: boolean
  fileInfo: ExcelFileInfo
  stores: StoreInfo[]
  summary: any
  storeData: Record<string, Record<string, MetricData>>
  loading?: boolean
  selectedMonth?: string
}

interface Emits {
  (e: 'update:open', value: boolean): void
  (e: 'confirm', data: any): void
  (e: 'cancel'): void
  (e: 'view-details', data: any): void
}

const props = withDefaults(defineProps<Props>(), {
  open: false,
  fileInfo: () => ({ name: '', path: '', size_mb: 0 }),
  stores: () => [],
  summary: () => ({ total_stores: 0 }),
  storeData: () => ({}),
  loading: false
})

const emit = defineEmits<Emits>()

// 响应式数据
const visible = computed({
  get: () => props.open,
  set: (value) => emit('update:open', value)
})

// 使用props中的loading状态
const compareLoading = ref(false)

// 对比结果相关状态
const showComparisonResult = ref(false)
const comparisonErrors = ref([])
const comparisonWarnings = ref([])
const comparisonData = ref({})
const databaseInfo = ref({})

// 直接使用传入的selectedMonth，不再解析文件名
const detectedMonth = computed(() => props.selectedMonth || '')

// 门店表格列定义
const storeColumns = [
  {
    title: '门店名称',
    dataIndex: 'name',
    key: 'name',
    width: 200
  },
  {
    title: '工作表名',
    dataIndex: 'sheet_name',
    key: 'sheet_name',
    width: 150,
    align: 'center'
  },
  {
    title: '指标数量',
    dataIndex: 'metrics_count',
    key: 'metrics_count',
    width: 100,
    align: 'center'
  },
  {
    title: '操作',
    key: 'action',
    width: 80,
    align: 'center'
  }
]


// 计算属性：门店表格数据
const storeTableData = computed(() => {
  return props.stores.map(store => {
    const metricsCount = props.storeData[store.name] ? Object.keys(props.storeData[store.name]).length : 0
    return {
      key: store.name,
      name: store.name,
      sheet_name: store.sheet_name,
      metrics_count: metricsCount
    }
  })
})


// 查看门店详情
const viewStoreDetails = (storeName: string) => {
  // 触发查看详情的emit事件
  emit('view-details', {
    storeName,
    storeData: props.storeData[storeName],
    fileInfo: props.fileInfo
  })
}


// 已移除确认导入功能，Excel数据在读取时已自动处理

// 取消
const handleCancel = () => {
  emit('cancel')
  visible.value = false
}

// 对比导出
const handleCompareExport = async () => {
  try {
    compareLoading.value = true
    
    // 准备对比数据
    const compareData = {
      excel_data: props.storeData,
      stores: props.stores,
      target_month: getCurrentMonth(),
      excel_filename: props.fileInfo?.name || ''  // 添加Excel文件名
    }
    
    const response = await fetch(`${API_BASE_URL}/api/import/compare-and-export`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(compareData)
    })
    
    const result = await response.json()
    
    if (result.success) {
      if (result.has_errors) {
        // 保存对比结果数据
        comparisonErrors.value = result.errors || []
        comparisonWarnings.value = result.warnings || []
        comparisonData.value = result.comparison_data || {}
        databaseInfo.value = result.database_info || {}
        
        // 调试日志
        console.log('ExcelDataPreview: 接收到的数据库信息:', databaseInfo.value)
        console.log('ExcelDataPreview: 覆盖率:', databaseInfo.value?.coverage_rate)
        console.log('ExcelDataPreview: Excel日期数:', databaseInfo.value?.excel_dates_count)
        console.log('ExcelDataPreview: 可用日期数:', databaseInfo.value?.available_dates_count)
        
        // 显示对比结果Modal，同时关闭当前预览Modal
        showComparisonResult.value = true
        visible.value = false  // 关闭Excel数据预览Modal
      } else {
        // 导出成功
        message.success(`对比导出成功！文件：${result.file_name}`)
        console.log('导出摘要:', result.summary)
      }
    } else {
      message.error(`对比导出失败: ${result.message || '未知错误'}`)
    }
    
  } catch (error) {
    console.error('对比导出失败:', error)
    message.error('对比导出失败，请检查网络连接')
  } finally {
    compareLoading.value = false
  }
}

// 获取用户选择的月份
const getCurrentMonth = () => {
  // 使用用户选择的月份，而不是当前月份
  return props.selectedMonth || ''
}

// 继续导出已匹配的门店
const handleContinueExport = async (matchedData: any) => {
  try {
    // 调用后端API，只导出匹配成功的门店数据
    const response = await fetch(`${API_BASE_URL}/api/import/export-matched-data`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        comparison_data: matchedData,
        target_month: getCurrentMonth()
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      message.success(`已匹配门店对比导出成功！文件：${result.file_name}`)
      showComparisonResult.value = false
      console.log('导出摘要:', result.summary)
    } else {
      message.error(`导出失败: ${result.message || '未知错误'}`)
    }
    
  } catch (error) {
    console.error('继续导出失败:', error)
    message.error('导出失败，请检查网络连接')
  }
}
</script>

<style scoped>
.excel-data-preview {
  max-height: 600px;
  overflow-y: auto;
  position: relative;
}

.metrics-table {
  margin-bottom: 20px;
}

.ant-table-tbody > tr > td {
  padding: 8px 12px;
}

.ant-table-thead > tr > th {
  background-color: #fafafa;
  font-weight: 500;
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

.custom-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
}

.footer-tip {
  color: #666;
  font-size: 13px;
  flex: 1;
  margin-right: 16px;
}

.footer-buttons {
  display: flex;
  gap: 8px;
}
</style>

