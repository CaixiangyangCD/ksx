<template>
  <div class="search-bar">
    <a-form
      :model="searchForm"
      layout="inline"
    >
      <a-form-item label="查询日期">
        <a-date-picker
          v-model:value="searchDate"
          placeholder="选择日期"
          format="YYYY-MM-DD"
          :allow-clear="false"
          style="width: 200px"
        />
      </a-form-item>
      <a-form-item label="门店名称">
        <a-input
          v-model:value="searchForm.mdshow"
          placeholder="请输入门店名称"
          style="width: 200px"
          @press-enter="handleSearch"
        />
      </a-form-item>
      <a-form-item>
        <a-space>
          <a-button type="primary" @click="handleSearch" :loading="loading">
            <template #icon>
              <SearchOutlined />
            </template>
            查询
          </a-button>
          <a-button @click="handleClear">
            <template #icon>
              <ClearOutlined />
            </template>
            清空
          </a-button>
        </a-space>
      </a-form-item>
    </a-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { SearchOutlined, ClearOutlined } from '@ant-design/icons-vue'
import dayjs from 'dayjs'

interface Emits {
  (e: 'search', params: { date: string, mdshow: string }): void
  (e: 'clear'): void
}

const emit = defineEmits<Emits>()

const loading = ref(false)
const searchDate = ref(dayjs().subtract(1, 'day'))
const searchForm = reactive({
  mdshow: ''
})

// 防抖定时器
let debounceTimer: NodeJS.Timeout | null = null

const handleSearch = () => {
  const params = {
    date: searchDate.value.format('YYYY-MM-DD'),
    mdshow: searchForm.mdshow
  }
  emit('search', params)
}

// 防抖搜索函数
const debouncedSearch = () => {
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
  debounceTimer = setTimeout(() => {
    handleSearch()
  }, 500) // 500ms防抖延迟
}

const handleClear = () => {
  searchForm.mdshow = ''
  searchDate.value = dayjs().subtract(1, 'day')
  emit('clear')
}

// 监听日期变化，立即查询
watch(searchDate, () => {
  handleSearch()
})

// 监听门店名称变化，防抖查询
watch(() => searchForm.mdshow, () => {
  debouncedSearch()
})
</script>

<style scoped>
.search-bar {
  background: #fff;
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.search-bar .ant-form-item {
  margin-bottom: 0;
}

.search-bar .ant-form-item:not(:last-child) {
  margin-right: 16px;
}

@media (max-width: 768px) {
  .search-bar {
    padding: 12px;
  }
  
  .search-bar .ant-form-item {
    margin-bottom: 12px;
    margin-right: 0;
  }
}
</style>
