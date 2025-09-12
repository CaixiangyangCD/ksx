<template>
  <a-config-provider :locale="zhCN">
    <div id="app">
      <div class="app-container">
        <div class="container">
          <!-- 搜索栏 -->
          <SearchBar
            :loading="loading"
            @search="handleSearch"
            @clear="handleClear"
          />

          <!-- 操作栏 -->
          <ActionBar
            :total="pagination.total"
            :sync-loading="syncLoading"
            :batch-sync-loading="batchSyncLoading"
            :has-data="tableData.length > 0"
            @sync="handleSyncData"
            @batchSync="showBatchSyncModalHandler"
            @config="showStoreConfig"
            @fieldConfig="showFieldConfig"
            @export="exportData"
            @exportExcel="showExcelExport"
          />

          <!-- 数据表格 -->
          <DataTable
            :data-source="tableData"
            :loading="loading"
            :pagination="pagination"
            @change="handleTableChange"
          />
        </div>
      </div>

      <!-- 同步数据遮罩层 -->
      <SyncOverlay
        :loading="syncLoading"
        :progress="syncProgress"
        :status="syncStatus"
      />

      <!-- 错误Modal -->
      <ErrorModal v-model:open="showNoDataModal" :sync-result="syncResult" />

      <!-- 同步数据Modal -->
      <a-modal
        v-model:open="showSyncModal"
        title="同步数据"
        :width="500"
        @ok="handleSyncConfirm"
        @cancel="showSyncModal = false"
        :confirm-loading="syncLoading"
        ok-text="确认同步"
        cancel-text="取消"
      >
        <div class="sync-modal-content">
          <p style="margin-bottom: 16px; color: #666">
            选择要同步数据的日期，系统将启动爬虫程序获取该日期的业务数据。
          </p>
          <div class="date-picker-container">
            <label style="display: block; margin-bottom: 8px; font-weight: 500"
              >选择日期：</label
            >
            <a-date-picker
              v-model:value="syncDate"
              :disabled-date="disabledDate"
              placeholder="请选择日期"
              style="width: 100%"
              format="YYYY-MM-DD"
            />
          </div>
          <div
            class="sync-tip"
            style="
              margin-top: 12px;
              padding: 8px;
              background: #f6f8fa;
              border-radius: 4px;
              font-size: 12px;
              color: #666;
            "
          >
            <InfoCircleOutlined style="margin-right: 4px" />
            只能选择昨天和昨天以前的日期
          </div>
        </div>
      </a-modal>

      <!-- 范围同步数据Modal -->
      <a-modal
        v-model:open="showBatchSyncModal"
        title="范围同步数据"
        :width="700"
        @ok="handleBatchSyncConfirm"
        @cancel="showBatchSyncModal = false"
        :confirm-loading="batchSyncLoading"
        ok-text="确认开始同步"
        cancel-text="取消"
      >
        <div class="batch-sync-modal-content">
          <p style="margin-bottom: 16px; color: #666">
            选择要同步数据的日期范围，系统将在后台启动爬虫程序获取指定日期范围内的所有业务数据。
          </p>
          
          <!-- 日期范围预览 -->
          <div v-if="batchStartDate && batchEndDate" style="margin-bottom: 16px; padding: 12px; background: #f6ffed; border: 1px solid #b7eb8f; border-radius: 6px;">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
              <CalendarOutlined style="color: #52c41a; margin-right: 8px;" />
              <span style="font-weight: 500; color: #389e0d;">同步日期范围预览</span>
            </div>
            <div style="color: #52c41a; font-size: 14px;">
              <div>开始日期：{{ batchStartDate.format('YYYY年MM月DD日') }}</div>
              <div>结束日期：{{ batchEndDate.format('YYYY年MM月DD日') }}</div>
              <div style="margin-top: 4px; font-weight: 500;">
                共 {{ batchEndDate.diff(batchStartDate, 'day') + 1 }} 天的数据
              </div>
            </div>
          </div>
          <div class="date-range-container">
            <div style="display: flex; gap: 16px; align-items: center;">
              <div style="flex: 1;">
                <label style="display: block; margin-bottom: 8px; font-weight: 500"
                  >开始日期：</label
                >
                <a-date-picker
                  v-model:value="batchStartDate"
                  :disabled-date="disabledDate"
                  placeholder="请选择开始日期"
                  style="width: 100%"
                  format="YYYY-MM-DD"
                />
              </div>
              <div style="flex: 1;">
                <label style="display: block; margin-bottom: 8px; font-weight: 500"
                  >结束日期：</label
                >
                <a-date-picker
                  v-model:value="batchEndDate"
                  :disabled-date="disabledDate"
                  placeholder="请选择结束日期（可选）"
                  style="width: 100%"
                  format="YYYY-MM-DD"
                />
              </div>
            </div>
          </div>
          <div
            class="batch-sync-tip"
            style="
              margin-top: 16px;
              padding: 16px;
              background: #fff7e6;
              border: 1px solid #ffd591;
              border-radius: 6px;
              font-size: 13px;
              color: #d46b08;
            "
          >
            <div style="display: flex; align-items: flex-start; margin-bottom: 12px;">
              <InfoCircleOutlined style="margin-right: 8px; margin-top: 2px; color: #fa8c16;" />
              <span style="font-weight: 500; color: #d46b08;">重要提示</span>
            </div>
            <div style="line-height: 1.6;">
              <div style="margin-bottom: 8px;">
                <strong>• 后台执行：</strong>范围同步将在后台自动执行，无需等待完成即可关闭此窗口
              </div>
              <div style="margin-bottom: 8px;">
                <strong>• 分批存储：</strong>系统会边同步边存储数据，每200条自动保存一次，避免数据丢失
              </div>
              <div style="margin-bottom: 8px;">
                <strong>• 实时查看：</strong>可以随时刷新页面或选择日期来查看已同步的数据
              </div>
              <div style="margin-bottom: 8px;">
                <strong>• 时间预估：</strong>同步大量日期可能需要较长时间，请耐心等待
              </div>
              <div>
                <strong>• 单日同步：</strong>如果不选择结束日期，将只同步开始日期的数据
              </div>
            </div>
          </div>
        </div>
      </a-modal>

      <!-- 门店配置Modal -->
      <StoreConfigModal
        v-model:open="showStoreConfigModal"
        :stores="stores"
        :current-rule="currentRule"
        @save="handleSaveExportRule"
      />

      <FieldConfigModal
        v-model:open="showFieldConfigModal"
        :field-config="fieldConfig"
        :current-rule="currentFieldRule"
        @save="handleSaveFieldRule"
      />

      <ExcelExportModal
        v-model:open="showExcelExportModal"
        :current-store-rule="currentRule"
        :current-field-rule="currentFieldRule"
        :current-query-date="currentQueryDate"
        @export="handleExcelExport"
      />
    </div>
  </a-config-provider>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { message, Modal } from "ant-design-vue";
import { InfoCircleOutlined } from "@ant-design/icons-vue";
import zhCN from "ant-design-vue/es/locale/zh_CN";
import dayjs from "dayjs";
import DataTable from "./components/DataTable.vue";
import SearchBar from "./components/SearchBar.vue";
import ActionBar from "./components/ActionBar.vue";
import SyncOverlay from "./components/SyncOverlay.vue";
import ErrorModal from "./components/ErrorModal.vue";
import StoreConfigModal from "./components/StoreConfigModal.vue";
import FieldConfigModal from "./components/FieldConfigModal.vue";
import ExcelExportModal from "./components/ExcelExportModal.vue";
import type { DataItem } from "./types";

// API配置
const API_BASE_URL = "http://localhost:18888";

// 响应式数据
const loading = ref(false);
const syncLoading = ref(false);
const batchSyncLoading = ref(false);
const syncProgress = ref(0);
const syncStatus = ref("准备中...");
const tableData = ref<DataItem[]>([]);
const showNoDataModal = ref(false);
const syncResult = ref<any>(null);

// 同步数据Modal相关
const showSyncModal = ref(false);
const syncDate = ref(dayjs().subtract(1, "day")); // 默认昨天

// 批量同步数据Modal相关
const showBatchSyncModal = ref(false);
const batchStartDate = ref(dayjs().subtract(7, "day")); // 默认一周前
const batchEndDate = ref(dayjs().subtract(1, "day")); // 默认昨天

// 门店配置相关
const showStoreConfigModal = ref(false);
const stores = ref<any[]>([]);
const selectedStores = ref<number[]>([]);
const currentRule = ref<any>(null);

// 字段配置相关
const showFieldConfigModal = ref(false);
const fieldConfig = ref<Record<string, any>>({});
const currentFieldRule = ref<any>(null);

// Excel导出相关
const showExcelExportModal = ref(false);

// 搜索表单
const searchForm = reactive({
  mdshow: "",
});

// 当前查询日期
const currentQueryDate = ref<string>("");

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条数据`,
  pageSizeOptions: ["10", "20", "50", "100"],
  showSizeChangerText: "每页显示",
  showQuickJumperText: "跳至",
  showTotalText: "共",
  itemRender: undefined,
  simple: false,
});

// 数据加载
const loadData = async (page: number = 1, size: number = 10, date?: string) => {
  try {
    loading.value = true;
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
      mdshow: searchForm.mdshow,
    });

    // 添加日期参数
    if (date) {
      params.append("date_str", date);
    }

    const response = await fetch(`${API_BASE_URL}/api/data?${params}`);
    const result = await response.json();

    if (result.success) {
      tableData.value = result.data || [];
      pagination.current = result.page || page;
      pagination.pageSize = result.page_size || size;
      pagination.total = result.total || 0;
    } else {
      message.error(result.message || "数据加载失败");
    }
  } catch (error) {
    console.error("数据加载失败:", error);
    message.error("数据加载失败");
  } finally {
    loading.value = false;
  }
};

// 搜索处理
const handleSearch = (params: { date: string; mdshow: string }) => {
  searchForm.mdshow = params.mdshow;
  currentQueryDate.value = params.date;
  pagination.current = 1;
  loadData(1, pagination.pageSize, params.date);
};

// 清空处理
const handleClear = () => {
  searchForm.mdshow = "";
  // 清空时重置为昨天的日期
  const yesterday = dayjs().subtract(1, "day").format("YYYY-MM-DD");
  currentQueryDate.value = yesterday;
  pagination.current = 1;
  loadData(1, pagination.pageSize, yesterday);
};

// 表格变化处理
const handleTableChange = (pag: any) => {
  loadData(pag.current, pag.pageSize, currentQueryDate.value);
};

// 同步数据处理
const handleSyncData = async () => {
  // 显示同步数据Modal
  showSyncModal.value = true;
};

// 同步确认处理
const handleSyncConfirm = async () => {
  if (!syncDate.value) {
    message.error("请选择要同步的日期");
    return;
  }

  showSyncModal.value = false;

  try {
    syncLoading.value = true;
    syncProgress.value = 0;
    syncStatus.value = "准备中...";

    // 模拟进度更新
    const progressInterval = setInterval(() => {
      if (syncProgress.value < 90) {
        syncProgress.value += Math.random() * 10;
        syncStatus.value = "正在同步数据...";
      }
    }, 1000);

    const response = await fetch(`${API_BASE_URL}/api/sync-data`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        date: syncDate.value.format("YYYY-MM-DD"),
      }),
    });

    clearInterval(progressInterval);
    syncProgress.value = 100;
    syncStatus.value = "同步完成";

    const result = await response.json();

    // 添加调试信息
    console.log("🔍 同步API返回结果:", result);
    console.log("🔍 result.success:", result.success);
    console.log("🔍 result.message:", result.message);

    if (result.success) {
      // 同步成功的情况
      await loadData(1, pagination.pageSize, currentQueryDate.value);

      // 根据实际结果显示不同的提示信息
      if (result.total > 0) {
        message.success(`同步完成！新增 ${result.total} 条数据`);
      } else if (result.message === "数据已是最新") {
        message.success("同步完成！数据已是最新");
      } else {
        message.success("同步完成！");
      }
    } else {
      // 同步失败的情况
      // 强制显示调试信息
      // alert(`调试信息:\nsuccess: ${result.success}\nmessage: "${result.message}"\ntotal: ${result.total}`);

      // if (result.message && result.message.includes("没有业务数据")) {
      //   // 特殊处理没有数据的情况
      //   message.warning("当前同步日期没有数据，请选择其他日期");
      // } else {
      // 其他错误情况显示错误Modal
      syncResult.value = result;
      showNoDataModal.value = true;
      // }
    }
  } catch (error) {
    console.error("同步数据失败:", error);
    message.error(
      `同步数据失败: ${error instanceof Error ? error.message : "未知错误"}`
    );
  } finally {
    // 延迟关闭遮罩层，让用户看到完成状态
    setTimeout(() => {
      syncLoading.value = false;
      syncProgress.value = 0;
      syncStatus.value = "准备中...";
    }, 1500);
  }
};

// 显示批量同步Modal
const showBatchSyncModalHandler = () => {
  showBatchSyncModal.value = true;
};

// 批量同步确认处理
const handleBatchSyncConfirm = async () => {
  if (!batchStartDate.value) {
    message.error("请选择开始日期");
    return;
  }

  const startDate = batchStartDate.value.format("YYYY-MM-DD");
  const endDate = batchEndDate.value ? batchEndDate.value.format("YYYY-MM-DD") : null;

  // 验证日期范围
  if (endDate && batchStartDate.value.isAfter(batchEndDate.value)) {
    message.error("开始日期不能大于结束日期");
    return;
  }

  // 计算日期范围天数
  const dayCount = endDate ? batchEndDate.value.diff(batchStartDate.value, 'day') + 1 : 1;
  
  // 二次确认
  const confirmMessage = endDate 
    ? `确认要同步 ${startDate} 到 ${endDate} 共 ${dayCount} 天的数据吗？\n\n同步将在后台执行，您可以随时查看进度。`
    : `确认要同步 ${startDate} 这一天的数据吗？\n\n同步将在后台执行，您可以随时查看进度。`;

  // 使用 Ant Design 的 Modal.confirm 进行二次确认
  const { Modal } = await import('ant-design-vue');
  Modal.confirm({
    title: '确认开始范围同步',
    content: confirmMessage,
    okText: '确认开始',
    cancelText: '取消',
    onOk: async () => {
      await executeBatchSync(startDate, endDate);
    }
  });
};

const executeBatchSync = async (startDate: string, endDate: string | null) => {
  showBatchSyncModal.value = false;

  try {
    batchSyncLoading.value = true;

    const response = await fetch(`${API_BASE_URL}/api/batch-sync-data`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        start_date: startDate,
        end_date: endDate,
      }),
    });

    const result = await response.json();
    console.log("批量同步响应:", result);

    if (result.success) {
      const dayCount = endDate ? dayjs(endDate).diff(dayjs(startDate), 'day') + 1 : 1;
      message.success({
        content: `范围同步已开始执行！\n正在同步 ${startDate}${endDate ? ` 到 ${endDate}` : ''} 共 ${dayCount} 天的数据\n\n您可以随时刷新页面查看同步进度`,
        duration: 6
      });
    } else {
      message.error(result.message || "范围同步启动失败");
    }
  } catch (error) {
    console.error("范围同步失败:", error);
    message.error(
      `范围同步失败: ${error instanceof Error ? error.message : "未知错误"}`
    );
  } finally {
    batchSyncLoading.value = false;
  }
};

// 门店配置相关方法
const loadStores = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/stores`);
    const result = await response.json();
    if (result.success) {
      stores.value = result.data;
    } else {
      message.error("获取门店列表失败");
    }
  } catch (error) {
    console.error("获取门店列表失败:", error);
    message.error("获取门店列表失败");
  }
};

const loadExportRule = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/export-rule`);
    const result = await response.json();
    if (result.success) {
      currentRule.value = result.data;
      if (result.data && result.data.selected_stores) {
        selectedStores.value = [...result.data.selected_stores];
      } else {
        selectedStores.value = [];
      }
    } else {
      message.error("获取导出规则失败");
    }
  } catch (error) {
    console.error("获取导出规则失败:", error);
    message.error("获取导出规则失败");
  }
};

const showStoreConfig = async () => {
  await loadStores();
  await loadExportRule();
  showStoreConfigModal.value = true;
};

const handleSaveExportRule = async (selectedStoresList: number[]) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/export-rule`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        selected_stores: selectedStoresList,
      }),
    });

    const result = await response.json();
    if (result.success) {
      message.success("导出规则保存成功");
      await loadExportRule(); // 重新加载规则
      showStoreConfigModal.value = false;
    } else {
      message.error(result.message || "保存失败");
    }
  } catch (error) {
    console.error("保存导出规则失败:", error);
    message.error("保存导出规则失败");
  }
};

const exportData = async () => {
  try {
    // 检查是否有配置规则
    if (!currentRule.value) {
      // 没有配置规则，提示用户配置
      const confirmed = await new Promise((resolve) => {
        Modal.confirm({
          title: "导出配置",
          content:
            "您还没有配置导出规则，是否要导出所有数据？建议先配置需要导出的门店。",
          onOk: () => resolve(true),
          onCancel: () => resolve(false),
          okText: "导出所有数据",
          cancelText: "先配置规则",
        });
      });

      if (!confirmed) {
        showStoreConfig();
        return;
      }
    }

    // 执行导出
    const selectedStoresForExport = currentRule.value
      ? currentRule.value.selected_stores
      : [];

    const response = await fetch(`${API_BASE_URL}/api/export-data`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        selected_stores: selectedStoresForExport,
        rule_name: currentRule.value ? currentRule.value.rule_name : "全部数据",
      }),
    });

    const result = await response.json();
    if (result.success) {
      // 创建下载链接
      const blob = new Blob([result.csv_content], {
        type: "text/csv;charset=utf-8;",
      });
      const link = document.createElement("a");
      const url = URL.createObjectURL(blob);

      link.setAttribute("href", url);
      link.setAttribute("download", result.filename);
      link.style.visibility = "hidden";

      // 添加到页面并触发下载
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // 清理URL对象
      URL.revokeObjectURL(url);

      // 显示保存提示，让用户知道文件已准备好下载
      message.info(
        `文件已准备就绪: ${result.filename}，请在弹出的对话框中选择保存位置`
      );
    } else {
      message.error(result.message || "导出失败");
    }
  } catch (error) {
    console.error("导出数据失败:", error);
    message.error("导出数据失败");
  }
};

// Excel导出相关方法
const loadFieldConfig = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/export-fields`);
    const result = await response.json();
    if (result.success) {
      fieldConfig.value = result.data;
    } else {
      message.error("获取字段配置失败");
    }
  } catch (error) {
    console.error("获取字段配置失败:", error);
    message.error("获取字段配置失败");
  }
};

const loadFieldRule = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/export-field-rule`);
    const result = await response.json();
    if (result.success) {
      currentFieldRule.value = result.data;
    } else {
      message.error("获取字段规则失败");
    }
  } catch (error) {
    console.error("获取字段规则失败:", error);
    message.error("获取字段规则失败");
  }
};

const showFieldConfig = async () => {
  await loadFieldConfig();
  await loadFieldRule();
  showFieldConfigModal.value = true;
};

const showExcelExport = async () => {
  await loadFieldConfig();
  await loadFieldRule();
  await loadExportRule(); // 加载最新的门店规则
  showExcelExportModal.value = true;
};

const handleSaveFieldRule = async (selectedFields: string[]) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/export-field-rule`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        selected_fields: selectedFields,
      }),
    });

    const result = await response.json();
    if (result.success) {
      message.success(
        `字段配置保存成功！已选择 ${selectedFields.length} 个字段`
      );
      await loadFieldRule(); // 重新加载规则
    } else {
      message.error(result.message || "保存失败");
    }
  } catch (error) {
    console.error("保存字段规则失败:", error);
    message.error("保存字段规则失败");
  }
};

const handleExcelExport = async (selectedDate: any = null) => {
  try {
    // 检查是否有配置规则
    if (!currentRule.value) {
      const confirmed = await new Promise((resolve) => {
        Modal.confirm({
          title: "导出配置",
          content:
            "您还没有配置导出规则，是否要导出所有数据？建议先配置需要导出的门店。",
          onOk: () => resolve(true),
          onCancel: () => resolve(false),
          okText: "导出所有数据",
          cancelText: "先配置规则",
        });
      });

      if (!confirmed) {
        showStoreConfig();
        return;
      }
    }

    // 准备请求数据
    const requestData: any = {};

    // 添加日期参数
    if (selectedDate) {
      requestData.date = selectedDate.format("YYYY-MM-DD");
    }

    const response = await fetch(`${API_BASE_URL}/api/export-excel`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestData),
    });

    const result = await response.json();
    if (result.success) {
      // 显示文件位置信息
      message.success({
        content: `Excel文件导出成功！\n文件名：${result.filename}\n保存位置：${result.file_path}\n共导出 ${result.count} 条记录`,
        duration: 8,
      });
      showExcelExportModal.value = false;
    } else {
      message.error(result.message || "导出失败");
    }
  } catch (error) {
    console.error("导出Excel数据失败:", error);
    message.error("导出Excel数据失败");
  }
};

// 禁用日期选择（只能选择昨天和昨天以前）
const disabledDate = (current: any) => {
  const yesterday = dayjs().subtract(1, "day");
  return current && current > yesterday;
};

// 页面加载时初始化数据
onMounted(() => {
  // 使用昨天的日期作为默认查询日期
  const yesterday = dayjs().subtract(1, "day").format("YYYY-MM-DD");
  currentQueryDate.value = yesterday;
  loadData(1, 10, yesterday);
  loadExportRule(); // 加载导出规则
  loadFieldRule(); // 加载字段规则
});
</script>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.app-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  padding: 32px !important;
}

@media (max-width: 768px) {
  .app-container {
    padding: 10px;
  }
}
</style>
