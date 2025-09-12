<template>
  <Modal
    v-model:open="visible"
    :title="errorTitle"
    width="500px"
    :footer="null"
    centered
    @cancel="handleClose"
  >
    <div class="error-modal">
      <div class="error-icon">
        {{ errorIcon }}
      </div>
      <div class="error-content">
        <h3 class="error-title">{{ errorTitle }}</h3>
        <p class="error-message">{{ errorMessage }}</p>
        
        <div v-if="errorReasons.length > 0" class="error-reasons">
          <h4>可能的原因：</h4>
          <ul>
            <li v-for="reason in errorReasons" :key="reason">{{ reason }}</li>
          </ul>
        </div>
        
        <div v-if="errorActions.length > 0" class="error-actions">
          <h4>建议操作：</h4>
          <ul>
            <li v-for="action in errorActions" :key="action">{{ action }}</li>
          </ul>
        </div>
      </div>
      
      <div class="error-modal-actions">
        <a-button type="primary" @click="handleClose">
          我知道了
        </a-button>
      </div>
    </div>
  </Modal>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { Modal } from 'ant-design-vue'

interface Props {
  open: boolean
  syncResult: any
}

interface Emits {
  (e: 'update:open', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visible = ref(false)

watch(() => props.open, (newVal) => {
  visible.value = newVal
})

watch(visible, (newVal) => {
  emit('update:open', newVal)
})

const handleClose = () => {
  visible.value = false
}

// 错误处理函数
const getErrorIcon = () => {
  if (!props.syncResult) return '⚠️'
  const message = props.syncResult.message || ''
  if (message.includes('没有数据')) return '📅'
  if (message.includes('登录失败') || message.includes('用户名') || message.includes('密码')) return '🔐'
  if (message.includes('超时') || message.includes('网络')) return '🌐'
  if (message.includes('浏览器') || message.includes('启动失败')) return '🌍'
  if (message.includes('提取失败') || message.includes('数据提取')) return '📊'
  return '⚠️'
}

const getErrorTitle = () => {
  if (!props.syncResult) return '同步失败'
  const message = props.syncResult.message || ''
  if (message.includes('没有数据')) {
    // 从消息中提取日期信息，或者使用默认的昨天日期
    let targetDateStr = '昨天'
    
    // 尝试从消息中提取日期
    const dateMatch = message.match(/(\d{4}-\d{2}-\d{2})/)
    if (dateMatch) {
      const dateStr = dateMatch[1]
      const date = new Date(dateStr)
      targetDateStr = date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    } else {
      // 如果没有找到日期，使用昨天的日期
      const yesterday = new Date()
      yesterday.setDate(yesterday.getDate() - 1)
      targetDateStr = yesterday.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    }
    
    return `没有数据 (${targetDateStr})`
  }
  if (message.includes('登录失败') || message.includes('用户名') || message.includes('密码')) return '登录失败'
  if (message.includes('超时') || message.includes('网络')) return '网络超时'
  if (message.includes('浏览器') || message.includes('启动失败')) return '爬虫启动失败'
  if (message.includes('提取失败') || message.includes('数据提取')) return '数据提取失败'
  return '同步失败'
}

const getErrorMessage = () => {
  return props.syncResult?.message || '未知错误'
}

const getErrorReasons = () => {
  if (!props.syncResult) return []
  const message = props.syncResult.message || ''
  
  if (message.includes('没有数据')) {
    // 从消息中提取日期信息，或者使用默认的昨天日期
    let targetDateStr = '昨天'
    
    // 尝试从消息中提取日期
    const dateMatch = message.match(/(\d{4}-\d{2}-\d{2})/)
    if (dateMatch) {
      const dateStr = dateMatch[1]
      const date = new Date(dateStr)
      targetDateStr = date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    } else {
      // 如果没有找到日期，使用昨天的日期
      const yesterday = new Date()
      yesterday.setDate(yesterday.getDate() - 1)
      targetDateStr = yesterday.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    }
    
    return [
      `同步功能只能获取昨天和昨天以前的业务数据`,
      `系统尝试获取 ${targetDateStr} 的数据，但未找到业务数据`,
      '请联系系统管理员确认该日期的数据是否已录入系统'
    ]
  }
  
  if (message.includes('登录失败') || message.includes('用户名') || message.includes('密码')) {
    return [
      '用户名或密码错误',
      '账户可能被锁定',
      '网络连接问题'
    ]
  }
  
  if (message.includes('超时') || message.includes('网络')) {
    return [
      '网络连接不稳定',
      '服务器响应超时',
      '网络环境问题'
    ]
  }
  
  if (message.includes('浏览器') || message.includes('启动失败')) {
    return [
      '浏览器环境问题',
      'Playwright浏览器未正确安装',
      '系统权限不足'
    ]
  }
  
  if (message.includes('提取失败') || message.includes('数据提取')) {
    return [
      '网站结构发生变化',
      '数据格式不匹配',
      '网络连接中断'
    ]
  }
  
  return ['未知错误原因']
}

const getErrorActions = () => {
  if (!props.syncResult) return []
  const message = props.syncResult.message || ''
  
  if (message.includes('没有数据')) {
    return [
      '检查日期设置',
      '联系管理员确认数据状态',
      '稍后重试'
    ]
  }
  
  if (message.includes('登录失败') || message.includes('用户名') || message.includes('密码')) {
    return [
      '检查用户名和密码',
      '联系管理员重置密码',
      '检查账户状态'
    ]
  }
  
  if (message.includes('超时') || message.includes('网络')) {
    return [
      '检查网络连接',
      '稍后重试',
      '联系网络管理员'
    ]
  }
  
  if (message.includes('浏览器') || message.includes('启动失败')) {
    return [
      '重新安装浏览器',
      '检查系统权限',
      '联系技术支持'
    ]
  }
  
  if (message.includes('提取失败') || message.includes('数据提取')) {
    return [
      '检查网站是否正常',
      '联系技术支持',
      '稍后重试'
    ]
  }
  
  return ['稍后重试', '联系管理员']
}

const errorIcon = computed(() => getErrorIcon())
const errorTitle = computed(() => getErrorTitle())
const errorMessage = computed(() => getErrorMessage())
const errorReasons = computed(() => getErrorReasons())
const errorActions = computed(() => getErrorActions())
</script>

<style scoped>
.error-modal {
  text-align: center;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-content {
  margin-bottom: 24px;
}

.error-title {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.error-message {
  margin: 0 0 20px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.error-reasons,
.error-actions {
  text-align: left;
  margin-bottom: 16px;
  
  h4 {
    margin: 0 0 8px 0;
    font-size: 14px;
    font-weight: 600;
    color: #333;
  }
  
  ul {
    margin: 0;
    padding-left: 20px;
    
    li {
      margin-bottom: 4px;
      font-size: 13px;
      color: #666;
      line-height: 1.4;
    }
  }
}

.error-modal-actions {
  text-align: center;
}

.error-modal-actions .ant-btn {
  min-width: 120px;
  height: 40px;
  border-radius: 6px;
  font-weight: 500;
}
</style>
