<template>
  <div id="app">
    <a-layout>
      <a-layout-header class="header">
        <h1 class="title">KSX门店管理系统</h1>
      </a-layout-header>
      
      <a-layout-content class="content">
        <div class="container">
          <!-- 搜索栏 -->
          <div class="search-bar">
            <a-form layout="inline" :model="searchForm">
              <a-form-item label="门店名称">
                <a-input 
                  v-model:value="searchForm.mdshow" 
                  placeholder="请输入门店名称进行搜索"
                  allowClear
                  style="width: 200px"
                />
              </a-form-item>
              <a-form-item label="查询日期">
                <a-date-picker 
                  v-model:value="searchForm.date"
                  placeholder="选择查询日期"
                  style="width: 150px"
                />
              </a-form-item>
              <a-form-item>
                <a-space>
                  <a-button 
                    type="primary" 
                    :loading="loading"
                    @click="handleSearch"
                  >
                    <template #icon>
                      <SearchOutlined />
                    </template>
                    搜索
                  </a-button>
                  <a-button @click="handleReset">
                    <template #icon>
                      <ReloadOutlined />
                    </template>
                    重置
                  </a-button>
                </a-space>
              </a-form-item>
            </a-form>
          </div>
          
          <!-- 操作按钮 -->
          <div class="action-bar">
            <a-space>
              <a-button 
                type="primary" 
                :loading="loading"
                @click="loadData"
              >
                <template #icon>
                  <ReloadOutlined />
                </template>
                刷新数据
              </a-button>
              <a-button 
                type="default" 
                :disabled="!tableData.length"
                @click="handleExport"
              >
                <template #icon>
                  <DownloadOutlined />
                </template>
                导出数据
              </a-button>
            </a-space>
            
            <div class="data-info">
              共 <a-tag color="blue">{{ pagination.total }}</a-tag> 条数据
            </div>
          </div>
          
          <!-- 数据表格 -->
          <DataTable
            :data-source="tableData"
            :loading="loading"
            :pagination="pagination"
            @change="handleTableChange"
          />
        </div>
      </a-layout-content>
    </a-layout>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { SearchOutlined, ReloadOutlined, DownloadOutlined } from '@ant-design/icons-vue'
import DataTable from './components/DataTable.vue'
import type { DataItem } from './types'
import dayjs, { Dayjs } from 'dayjs'

// 响应式数据
const loading = ref(false)
const tableData = ref<DataItem[]>([])

// 搜索表单
const searchForm = reactive({
  mdshow: '',
  date: null as Dayjs | null
})

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number, range: [number, number]) => 
    `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
  pageSizeOptions: ['10', '20', '50', '100'],
  size: 'default' as const
})

// API配置
const API_BASE_URL = 'http://127.0.0.1:8080'

// 真实API数据加载
const loadData = async (page = 1, pageSize = 10) => {
  loading.value = true
  try {
    // 构建API请求参数
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString()
    })
    
    // 添加搜索条件
    if (searchForm.mdshow) {
      params.append('mdshow', searchForm.mdshow)
    }
    
    // 添加日期条件
    if (searchForm.date) {
      params.append('date_str', searchForm.date.format('YYYY-MM-DD'))
    }
    
    // 发送API请求
    const response = await fetch(`${API_BASE_URL}/api/data?${params}`)
    
    if (!response.ok) {
      throw new Error(`HTTP错误: ${response.status}`)
    }
    
    const result = await response.json()
    
    if (result.success) {
      // 更新分页信息
      pagination.total = result.total
      pagination.current = result.page
      pagination.pageSize = result.page_size
      
      // 更新数据
      tableData.value = result.data || []
      
      console.log(`加载数据成功: ${result.data?.length || 0} 条记录`)
      
      if (page === 1) {
        message.success(`加载数据成功，共 ${result.total} 条记录`)
      }
    } else {
      throw new Error(result.message || '加载数据失败')
    }
    
  } catch (error) {
    console.error('加载数据失败:', error)
    message.error(`加载数据失败: ${error instanceof Error ? error.message : '未知错误'}`)
    
    // 清空数据
    tableData.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  pagination.current = 1
  loadData(1, pagination.pageSize)
}

// 重置处理
const handleReset = () => {
  searchForm.mdshow = ''
  searchForm.date = null
  pagination.current = 1
  loadData(1, pagination.pageSize)
}

// 导出处理
const handleExport = () => {
  try {
    // 生成CSV内容
    const csvContent = generateCSV(tableData.value)
    downloadCSV(csvContent, `ksx_data_export_${dayjs().format('YYYY-MM-DD')}.csv`)
    message.success('数据导出成功')
  } catch (error) {
    message.error('导出失败')
  }
}

// 表格变化处理
const handleTableChange = (pag: any) => {
  loadData(pag.current, pag.pageSize)
}

// CSV生成函数
const generateCSV = (data: DataItem[]): string => {
  if (!data.length) return ''
  
  // 获取表头
  const headers = Object.keys(data[0])
  
  // 生成CSV内容
  const csvRows = [
    headers.join(','),  // 表头
    ...data.map(row => 
      headers.map(header => {
        const value = (row as any)[header]
        // 处理包含逗号或引号的值
        if (value && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`
        }
        return value || ''
      }).join(',')
    )
  ]
  
  return csvRows.join('\n')
}

// CSV下载函数
const downloadCSV = (content: string, filename: string) => {
  // 添加BOM以支持中文
  const BOM = '\uFEFF'
  const blob = new Blob([BOM + content], { type: 'text/csv;charset=utf-8' })
  
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(link.href)
}

// 页面加载时初始化数据
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  padding: 0 24px;
}

.title {
  margin: 0;
  color: #1890ff;
  font-size: 24px;
}

.content {
  padding: 24px;
  min-height: calc(100vh - 64px);
  background: #f0f2f5;
}

.container {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.search-bar {
  margin-bottom: 24px;
  padding: 16px;
  background: #fafafa;
  border-radius: 6px;
  border: 1px solid #d9d9d9;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.data-info {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #666;
}

/* 全局样式重置 */
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content {
    padding: 16px;
  }
  
  .container {
    padding: 16px;
  }
  
  .action-bar {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .search-bar .ant-form {
    flex-direction: column;
  }
  
  .search-bar .ant-form-item {
    margin-bottom: 16px;
  }
}
</style>