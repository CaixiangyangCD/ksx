<template>
  <a-modal
    v-model:open="visible"
    title="数据对比结果"
    :width="1200"
    @cancel="handleCancel"
    :z-index="1500"
    :mask-closable="false"
  >
    <template #footer>
      <div class="result-footer">
        <a-button @click="handleCancel">关闭</a-button>
        <a-button
          v-if="hasMatchedStores"
          type="primary"
          @click="handleContinueExport"
          :loading="exportLoading"
          :disabled="isExportDisabled"
        >
          继续导出已匹配门店
        </a-button>
      </div>
    </template>

    <div class="comparison-result">
      <!-- 总体统计 -->
      <div class="summary-section">
        <h3
          style="
            margin: 0 0 16px 0;
            color: #262626;
            font-size: 16px;
            font-weight: 600;
          "
        >
          <CheckCircleOutlined style="margin-right: 8px; color: #52c41a" />
          对比结果概览
        </h3>
        <div class="summary-cards">
          <div class="summary-card success">
            <div class="card-icon">
              <CheckCircleOutlined />
            </div>
            <div class="card-content">
              <div class="count">{{ matchedStores.length }}</div>
              <div class="label">匹配成功</div>
            </div>
          </div>
          <div class="summary-card error">
            <div class="card-icon">
              <CloseCircleOutlined />
            </div>
            <div class="card-content">
              <div class="count">{{ unmatchedStores.length }}</div>
              <div class="label">匹配失败</div>
            </div>
          </div>
          <div class="summary-card warning">
            <div class="card-icon">
              <ExclamationCircleOutlined />
            </div>
            <div class="card-content">
              <div class="count">{{ multipleMatchStores.length }}</div>
              <div class="label">多重匹配</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 数据库信息 -->
      <div v-if="databaseInfo" class="database-info-card">
        <h4>
          <DatabaseOutlined style="margin-right: 8px" />
          数据库文件覆盖情况 ({{ databaseInfo.target_month }})
        </h4>

        <div class="coverage-stats">
          <div
            class="stat-item"
            :class="{ warning: databaseInfo.has_coverage_issues }"
          >
            <span class="stat-label">数据库覆盖率：</span>
            <span class="stat-value"
              >{{
                isNaN(databaseInfo.coverage_rate)
                  ? "0"
                  : Math.round((databaseInfo.coverage_rate || 0) * 100)
              }}%</span
            >
          </div>
          <div class="stat-item">
            <span class="stat-label">Excel包含日期：</span>
            <span class="stat-value"
              >{{
                databaseInfo.excel_dates_count ||
                databaseInfo.excel_dates?.length ||
                0
              }}
              天</span
            >
          </div>
          <div class="stat-item success">
            <span class="stat-label">数据库可用：</span>
            <span class="stat-value"
              >{{
                databaseInfo.available_dates_count ||
                databaseInfo.available_dates?.length ||
                0
              }}
              天</span
            >
          </div>
          <div
            class="stat-item error"
            v-if="
              (databaseInfo.missing_dates_count ||
                databaseInfo.missing_dates?.length) > 0
            "
          >
            <span class="stat-label">数据库缺失：</span>
            <span class="stat-value"
              >{{
                databaseInfo.missing_dates_count ||
                databaseInfo.missing_dates?.length ||
                0
              }}
              天</span
            >
          </div>
        </div>

        <!-- 详细的日期信息 -->
        <div class="database-details">
          <a-row :gutter="16">
            <a-col :span="12" v-if="databaseInfo.available_dates?.length > 0">
              <div class="date-section available">
                <h5>
                  <CheckCircleOutlined
                    style="color: #52c41a; margin-right: 4px"
                  />
                  可用数据库文件 ({{ databaseInfo.available_dates.length }} 天)
                </h5>
                <div class="date-tags">
                  <a-tag
                    v-for="date in databaseInfo.available_dates"
                    :key="`available-${date}`"
                    color="green"
                    size="small"
                  >
                    {{ getDatabaseDateLabel(date) }}
                  </a-tag>
                </div>
              </div>
            </a-col>
            <a-col :span="12" v-if="databaseInfo.missing_dates?.length > 0">
              <div class="date-section missing">
                <h5>
                  <ExclamationCircleOutlined
                    style="color: #ff4d4f; margin-right: 4px"
                  />
                  缺失数据库文件 ({{ databaseInfo.missing_dates.length }} 天)
                </h5>
                <div class="date-tags">
                  <a-tag
                    v-for="date in databaseInfo.missing_dates"
                    :key="`missing-${date}`"
                    color="red"
                    size="small"
                  >
                    {{ getDatabaseDateLabel(date) }}
                  </a-tag>
                </div>
              </div>
            </a-col>
          </a-row>
        </div>

        <div
          class="coverage-message"
          :class="{ warning: databaseInfo.has_coverage_issues }"
        >
          <ExclamationCircleOutlined
            v-if="databaseInfo.has_coverage_issues"
            style="margin-right: 8px"
          />
          <CheckCircleOutlined v-else style="margin-right: 8px" />
          {{ databaseInfo.message || "数据库覆盖检查完成" }}
        </div>

        <!-- 日期偏移说明 -->
        <div v-if="databaseInfo.date_offset_note" class="date-offset-note">
          <a-alert type="info" show-icon style="margin-top: 8px">
            <template #message>日期对应关系说明</template>
            <template #description>
              {{ databaseInfo.date_offset_note }}
            </template>
          </a-alert>
        </div>

        <!-- 同步数据建议和操作 -->
        <div
          v-if="databaseInfo.has_coverage_issues"
          class="sync-recommendation"
        >
          <a-alert
            :type="coverageRate === 0 ? 'error' : 'warning'"
            show-icon
            style="margin-top: 12px"
          >
            <template #message>
              <span v-if="coverageRate === 0">数据库文件完全缺失</span>
              <span v-else>数据库文件不完整</span>
            </template>
            <template #description>
              <div style="margin-bottom: 12px">
                <p v-if="coverageRate === 0">
                  系统检测到Excel文件包含
                  <strong>{{ databaseInfo.excel_dates_count || 0 }} 天</strong>
                  的数据， 但对应的数据库文件完全缺失。无法进行数据对比。
                </p>
                <p v-else>
                  Excel文件包含
                  <strong>{{ databaseInfo.excel_dates_count || 0 }} 天</strong>
                  的数据， 但数据库中只有
                  <strong
                    >{{ databaseInfo.available_dates_count || 0 }} 天</strong
                  >
                  的文件可用， 缺失
                  <strong
                    >{{ databaseInfo.missing_dates_count || 0 }} 天</strong
                  >
                  的数据。
                </p>
                <p style="margin-top: 8px; color: #1890ff">
                  <BulbOutlined style="margin-right: 4px" />
                  建议先执行批量同步数据操作，生成缺失的数据库文件后再进行对比。
                </p>
              </div>
            </template>
          </a-alert>
        </div>

        <!-- 覆盖率良好的提示 -->
        <div
          v-else-if="databaseInfo.excel_dates_count > 0"
          class="coverage-good"
        >
          <a-alert
            message="数据库文件完整"
            description="所有Excel日期都有对应的数据库文件，可以正常进行数据对比。"
            type="success"
            show-icon
            style="margin-top: 12px"
          />
        </div>
      </div>

      <!-- 详细结果 -->
      <a-tabs v-model:active-key="activeTab" type="card">
        <!-- 匹配成功的门店 -->
        <a-tab-pane
          key="matched"
          tab="匹配成功"
          v-if="matchedStores.length > 0"
        >
          <div class="matched-stores">
            <a-list :data-source="matchedStores" size="small">
              <template #renderItem="{ item }">
                <a-list-item>
                  <div class="store-match-item success">
                    <div class="excel-store">{{ item.excelStore }}</div>
                    <div class="arrow">→</div>
                    <div class="db-store">{{ item.dbStore }}</div>
                    <div class="data-count">{{ item.dataCount }} 天数据</div>
                  </div>
                </a-list-item>
              </template>
            </a-list>
          </div>
        </a-tab-pane>

        <!-- 匹配失败的门店 -->
        <a-tab-pane
          key="unmatched"
          tab="匹配失败"
          v-if="unmatchedStores.length > 0"
        >
          <a-alert type="error" show-icon style="margin-bottom: 16px">
            <template #message>
              <span
                >以下门店在数据库中未找到匹配项，请检查门店名称是否正确</span
              >
            </template>
          </a-alert>
          <a-list :data-source="unmatchedStores" size="small">
            <template #renderItem="{ item }">
              <a-list-item>
                <div class="store-match-item error">
                  <div class="excel-store">{{ item.excelStore }}</div>
                  <div class="error-message">{{ item.message }}</div>
                </div>
              </a-list-item>
            </template>
          </a-list>
        </a-tab-pane>

        <!-- 多重匹配的门店 -->
        <a-tab-pane
          key="multiple"
          tab="多重匹配"
          v-if="multipleMatchStores.length > 0"
        >
          <a-alert type="warning" show-icon style="margin-bottom: 16px">
            <template #message>
              <span>以下门店匹配到多个数据库门店，请手动确认</span>
            </template>
          </a-alert>
          <a-list :data-source="multipleMatchStores" size="small">
            <template #renderItem="{ item }">
              <a-list-item>
                <div class="store-match-item warning">
                  <div class="excel-store">{{ item.excelStore }}</div>
                  <div class="multiple-matches">
                    <div>可能匹配：</div>
                    <div class="matches-list">
                      <a-tag
                        v-for="match in item.matches"
                        :key="match"
                        color="orange"
                      >
                        {{ match }}
                      </a-tag>
                    </div>
                  </div>
                </div>
              </a-list-item>
            </template>
          </a-list>
        </a-tab-pane>
      </a-tabs>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import {
  DatabaseOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  BulbOutlined,
  SyncOutlined,
  ReloadOutlined,
} from "@ant-design/icons-vue";

interface ComparisonError {
  type: string;
  excel_store?: string;
  matched_stores?: string[];
  message: string;
}

interface Props {
  open: boolean;
  errors: ComparisonError[];
  warnings: ComparisonError[];
  comparisonData?: any;
  databaseInfo?: any;
}

interface Emits {
  (e: "update:open", value: boolean): void;
  (e: "continue-export", data: any): void;
  (e: "cancel"): void;
}

const props = withDefaults(defineProps<Props>(), {
  open: false,
  errors: () => [],
  warnings: () => [],
  comparisonData: () => ({}),
});

const emit = defineEmits<Emits>();

const visible = computed({
  get: () => props.open,
  set: (value) => emit("update:open", value),
});

// 调试日志：监听props变化
watch(
  () => props.databaseInfo,
  (newInfo) => {
    console.log("DataComparisonResultModal: databaseInfo changed:", newInfo);
    if (newInfo) {
      console.log(
        "DataComparisonResultModal: coverage_rate:",
        newInfo.coverage_rate
      );
      console.log(
        "DataComparisonResultModal: excel_dates_count:",
        newInfo.excel_dates_count
      );
      console.log(
        "DataComparisonResultModal: available_dates_count:",
        newInfo.available_dates_count
      );
      console.log(
        "DataComparisonResultModal: available_dates:",
        newInfo.available_dates
      );
      console.log(
        "DataComparisonResultModal: missing_dates:",
        newInfo.missing_dates
      );
    }
  },
  { immediate: true, deep: true }
);

const activeTab = ref("matched");
const exportLoading = ref(false);
const syncLoading = ref(false);

// 处理错误数据，分类显示
const matchedStores = computed(() => {
  const matched = [];
  for (const [storeName, storeData] of Object.entries(props.comparisonData)) {
    if (storeData && typeof storeData === "object" && storeData.db_store_name) {
      matched.push({
        excelStore: storeName,
        dbStore: storeData.db_store_name,
        dataCount: Object.keys(storeData.daily_comparisons || {}).length,
      });
    }
  }
  return matched;
});

const unmatchedStores = computed(() => {
  return props.errors
    .filter((error) => error.type === "store_not_found")
    .map((error) => ({
      excelStore: error.excel_store,
      message: error.message,
    }));
});

const multipleMatchStores = computed(() => {
  return props.errors
    .filter((error) => error.type === "multiple_stores_found")
    .map((error) => ({
      excelStore: error.excel_store,
      matches: error.matched_stores || [],
    }));
});

const hasMatchedStores = computed(() => matchedStores.value.length > 0);

// 计算是否应该禁用导出按钮
const isExportDisabled = computed(() => {
  // 如果没有数据库信息，允许导出
  if (!props.databaseInfo) return false;

  // 如果覆盖率为0或所有日期都缺失，禁用导出
  const coverageRate = props.databaseInfo.coverage_rate || 0;
  const hasAvailableDates =
    (props.databaseInfo.available_dates_count ||
      props.databaseInfo.available_dates?.length ||
      0) > 0;

  return coverageRate === 0 || !hasAvailableDates;
});

// 自动选择默认Tab
const defaultTab = computed(() => {
  if (matchedStores.value.length > 0) return "matched";
  if (unmatchedStores.value.length > 0) return "unmatched";
  if (multipleMatchStores.value.length > 0) return "multiple";
  return "matched";
});

// 监听默认Tab变化
activeTab.value = defaultTab.value;

const handleCancel = () => {
  emit("cancel");
  visible.value = false;
};

const handleContinueExport = async () => {
  try {
    exportLoading.value = true;
    emit("continue-export", props.comparisonData);
  } finally {
    exportLoading.value = false;
  }
};

const handleSyncData = async () => {
  try {
    syncLoading.value = true;
    // TODO: 这里应该调用同步数据的API
    // 暂时显示提示信息
    console.log("触发批量同步数据操作");
    // 可以发射事件让父组件处理
    // emit('sync-data', props.databaseInfo)
  } finally {
    syncLoading.value = false;
  }
};

const handleRefreshCheck = () => {
  // 发射事件让父组件重新检查数据库覆盖
  console.log("重新检查数据库覆盖");
  // emit('refresh-check')
};

// 获取数据库日期标签（包含月份信息）
const getDatabaseDateLabel = (excelDate: string) => {
  if (!excelDate || !props.databaseInfo?.target_month) {
    return excelDate;
  }

  try {
    // Excel日期格式：如 "1日", "2日"
    const day = parseInt(excelDate.replace("日", ""));
    if (isNaN(day)) return excelDate;

    // 计算对应的数据库日期（Excel日期-1天）
    const [year, month] = props.databaseInfo.target_month
      .split("-")
      .map(Number);
    const excelDateTime = new Date(year, month - 1, day);
    const dbDateTime = new Date(excelDateTime.getTime() - 24 * 60 * 60 * 1000); // 减1天

    const dbYear = dbDateTime.getFullYear();
    const dbMonth = dbDateTime.getMonth() + 1;
    const dbDay = dbDateTime.getDate();

    // 如果跨月了，显示月份信息
    if (dbMonth !== month) {
      return `${dbMonth}-${dbDay}日`;
    } else {
      return `${dbDay}日`;
    }
  } catch (error) {
    console.warn("解析日期标签失败:", error);
    return excelDate;
  }
};
</script>

<style scoped>
.comparison-result {
  max-height: 600px;
  overflow-y: auto;
}

.summary-section {
  margin-bottom: 24px;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
  transition: all 0.3s ease;
}

.summary-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.summary-card.success {
  border-color: #b7eb8f;
  background: #f6ffed;
}

.summary-card.error {
  border-color: #ffccc7;
  background: #fff2f0;
}

.summary-card.warning {
  border-color: #ffd591;
  background: #fffbe6;
}

.card-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.8);
}

.summary-card.success .card-icon {
  color: #52c41a;
}

.summary-card.error .card-icon {
  color: #ff4d4f;
}

.summary-card.warning .card-icon {
  color: #faad14;
}

.card-content {
  flex: 1;
}

.card-content .count {
  font-size: 24px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
}

.card-content .label {
  font-size: 14px;
  color: #666;
  line-height: 1;
}

.database-info-card {
  margin-bottom: 24px;
  padding: 20px;
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 8px;
}

.database-info-card h4 {
  margin: 0 0 16px 0;
  color: #52c41a;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.coverage-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
  border: 1px solid #d9d9d9;
}

.stat-item.warning {
  background: #fff7e6;
  border-color: #ffd591;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.stat-value {
  font-weight: 600;
  font-size: 14px;
}

.stat-value.error {
  color: #ff4d4f;
}

.coverage-message {
  padding: 12px 16px;
  background: white;
  border: 1px solid #b7eb8f;
  border-radius: 6px;
  margin-bottom: 16px;
  color: #52c41a;
  display: flex;
  align-items: center;
}

.coverage-message.warning {
  background: #fff7e6;
  border-color: #ffd591;
  color: #fa8c16;
}

.coverage-suggestion {
  padding: 12px 16px;
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 6px;
  color: #1890ff;
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.database-details {
  margin-top: 16px;
}

.date-section {
  margin-bottom: 16px;
}

.date-section h5 {
  margin-bottom: 8px;
  font-weight: 500;
  display: flex;
  align-items: center;
}

.date-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.date-tags .ant-tag {
  margin: 0;
}

.sync-recommendation .sync-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.stat-item.success .stat-value {
  color: #52c41a;
}

.stat-item.error .stat-value {
  color: #ff4d4f;
}

.missing-dates h5 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #666;
}

.date-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.summary-item {
  text-align: center;
  flex: 1;
}

.summary-item .count {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
}

.summary-item .label {
  color: #666;
  font-size: 14px;
}

.summary-item.success .count {
  color: #52c41a;
}

.summary-item.error .count {
  color: #f5222d;
}

.summary-item.warning .count {
  color: #fa8c16;
}

.store-match-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  width: 100%;
}

.store-match-item.success {
  border-left: 3px solid #52c41a;
  padding-left: 12px;
}

.store-match-item.error {
  border-left: 3px solid #f5222d;
  padding-left: 12px;
}

.store-match-item.warning {
  border-left: 3px solid #fa8c16;
  padding-left: 12px;
}

.excel-store {
  font-weight: 500;
  color: #1890ff;
  min-width: 120px;
}

.arrow {
  color: #52c41a;
  font-weight: bold;
}

.db-store {
  color: #52c41a;
  font-weight: 500;
  min-width: 120px;
}

.data-count {
  color: #666;
  font-size: 12px;
  margin-left: auto;
}

.error-message {
  color: #f5222d;
  font-size: 13px;
  flex: 1;
}

.multiple-matches {
  flex: 1;
}

.matches-list {
  margin-top: 4px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.result-footer {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.matched-stores,
.unmatched-stores,
.multiple-stores {
  max-height: 400px;
  overflow-y: auto;
}
</style>
