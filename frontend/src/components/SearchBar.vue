<template>
  <div class="search-bar">
    <a-form layout="inline" :model="searchForm" @finish="handleSearch">
      <a-form-item label="区域">
        <a-select
          v-model:value="searchForm.area"
          placeholder="请选择区域"
          style="width: 120px"
          allow-clear
        >
          <a-select-option value="1区">1区</a-select-option>
          <a-select-option value="2区">2区</a-select-option>
          <a-select-option value="3区">3区</a-select-option>
          <a-select-option value="4区">4区</a-select-option>
          <a-select-option value="5区">5区</a-select-option>
        </a-select>
      </a-form-item>
      
      <a-form-item label="门店名称">
        <a-input
          v-model:value="searchForm.MDShow"
          placeholder="请输入门店名称"
          style="width: 200px"
          allow-clear
        />
      </a-form-item>
      
      <a-form-item label="日期范围">
        <a-range-picker
          v-model:value="searchForm.dateRange"
          style="width: 240px"
        />
      </a-form-item>
      
      <a-form-item>
        <a-button type="primary" html-type="submit" :loading="loading">
          <template #icon>
            <SearchOutlined />
          </template>
          搜索
        </a-button>
        <a-button style="margin-left: 8px" @click="handleReset">
          重置
        </a-button>
      </a-form-item>
    </a-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { SearchOutlined } from '@ant-design/icons-vue'
import type { SearchForm } from '../types'

interface Props {
  loading?: boolean
}

interface Emits {
  (e: 'search', form: SearchForm): void
  (e: 'reset'): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const emit = defineEmits<Emits>()

const searchForm = reactive<SearchForm>({
  area: undefined,
  MDShow: undefined,
  dateRange: undefined
})

const handleSearch = () => {
  emit('search', { ...searchForm })
}

const handleReset = () => {
  Object.assign(searchForm, {
    area: undefined,
    MDShow: undefined,
    dateRange: undefined
  })
  emit('reset')
}
</script>

<style scoped>
.search-bar {
  background: #fff;
  padding: 16px;
  border-radius: 6px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
}
</style>
