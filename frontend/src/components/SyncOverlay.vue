<template>
  <div v-if="loading" class="sync-overlay">
    <div class="sync-modal">
      <div class="sync-content">
        <div class="sync-icon">
          <div class="sync-spinner"></div>
        </div>
        <h3 class="sync-title">正在同步数据</h3>
        <p class="sync-message">爬虫程序正在运行，请稍候...</p>
        <div class="sync-progress">
          <a-progress 
            :percent="progress" 
            :show-info="false"
            stroke-color="#1890ff"
          />
          <p class="progress-text">{{ status }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  loading: boolean
  progress: number
  status: string
}

defineProps<Props>()
</script>

<style scoped>
.sync-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.sync-modal {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  max-width: 400px;
  width: 90%;
  text-align: center;
}

.sync-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.sync-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sync-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f0f0f0;
  border-top: 4px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.sync-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.sync-message {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.sync-progress {
  width: 100%;
  max-width: 300px;
}

.progress-text {
  margin: 8px 0 0 0;
  font-size: 12px;
  color: #999;
}
</style>
