<template>
  <div class="db-task-runs-list">
    <!-- 头部：返回按钮 + 任务信息 -->
    <div class="header-section">
      <div class="header-left">
        <el-button v-if="showBackButton" @click="$emit('back')" type="default">
          ← 返回
        </el-button>
        <div v-if="taskInfo" class="task-info">
          <h2 class="task-name">{{ taskInfo.name }}</h2>
          <p class="task-desc">{{ taskInfo.description || '暂无描述' }}</p>
        </div>
      </div>
      <div class="header-right">
        <el-button
          @click="$emit('refresh')"
          :loading="loading"
          type="primary"
        >
          刷新
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <el-skeleton v-if="loading && runs.length === 0" :rows="5" animated />

    <!-- 空状态 -->
    <el-empty v-else-if="runs.length === 0" description="暂无运行记录" />

    <!-- 运行列表 -->
    <div v-else class="runs-container">
      <div
        v-for="run in runs"
        :key="run.run_id"
        class="run-card"
        :class="{ active: selectedRunId === run.run_id }"
        @click="toggleRun(run.run_id)"
      >
        <!-- 运行头部 -->
        <div class="run-header">
          <div class="run-main">
            <span class="run-title">运行 #{{ run.run_id }}</span>
            <el-tag :type="statusType(run.status)">{{ run.status }}</el-tag>
          </div>
          <div class="run-times">
            <span>{{ formatDate(run.started_at) }}</span>
            <span v-if="run.finished_at">结束: {{ formatDate(run.finished_at) }}</span>
          </div>
          <el-icon class="run-chevron" :class="{ expanded: selectedRunId === run.run_id }">
            <CaretBottom />
          </el-icon>
        </div>

        <!-- 运行展开内容 -->
        <div v-if="selectedRunId === run.run_id" class="run-content">
          <!-- 选项卡 -->
          <el-tabs v-model="activeTab" class="tabs-wrapper">
            <el-tab-pane label="执行日志" name="logs">
              <div v-if="currentRunLoading" class="loading-wrapper">
                <el-icon class="is-loading"><Loading /></el-icon>
                加载日志中...
              </div>
              <div v-else-if="currentLogs.length === 0" class="empty-tip">暂无日志</div>
              <div v-else class="logs-list">
                <div v-for="log in currentLogs" :key="log.script" class="log-item">
                  <div class="log-script">{{ log.script }}</div>
                  <pre class="log-output">{{ log.output }}</pre>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="环境变量" name="contexts">
              <div v-if="currentRunLoading" class="loading-wrapper">
                <el-icon class="is-loading"><Loading /></el-icon>
                加载环境变量中...
              </div>
              <div v-else-if="currentContexts.length === 0" class="empty-tip">暂无环境变量</div>
              <div v-else class="contexts-list">
                <div v-for="ctx in currentContexts" :key="ctx.script" class="context-item">
                  <div class="context-script">{{ ctx.script }}</div>
                  <pre class="context-data">{{ JSON.stringify(ctx.context, null, 2) }}</pre>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { CaretBottom, Loading } from '@element-plus/icons-vue'

interface Run {
  run_id: string | number
  status: string
  started_at: string
  finished_at?: string
}

interface TaskInfo {
  name: string
  description?: string
}

interface LogItem {
  script: string
  output: string
}

interface ContextItem {
  script: string
  context: Record<string, any>
}

defineProps<{
  runs: Run[]
  taskInfo?: TaskInfo | null
  loading: boolean
  showBackButton?: boolean
}>()

const emit = defineEmits<{
  back: []
  refresh: []
  viewLogs: [runId: string | number]
}>()

const selectedRunId = ref<string | number | null>(null)
const currentRunLoading = ref(false)
const activeTab = ref('logs')
const currentLogs = ref<LogItem[]>([])
const currentContexts = ref<ContextItem[]>([])

const toggleRun = (runId: string | number) => {
  if (selectedRunId.value === runId) {
    selectedRunId.value = null
  } else {
    loadRunDetails(runId)
  }
}

const loadRunDetails = (runId: string | number) => {
  selectedRunId.value = runId
  currentRunLoading.value = true
  activeTab.value = 'logs'
  emit('viewLogs', runId)
}

const updateRunDetails = (logs: LogItem[], contexts: ContextItem[]) => {
  currentLogs.value = logs || []
  currentContexts.value = contexts || []
  currentRunLoading.value = false
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const statusType = (status: string): 'primary' | 'success' | 'warning' | 'info' | 'danger' => {
  const typeMap: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    success: 'success',
    failed: 'danger',
    error: 'danger',
    timeout: 'danger',
    running: 'warning'
  }
  return typeMap[status] || 'info'
}

// 暴露方法以便父组件调用
defineExpose({
  updateRunDetails
})
</script>

<style scoped>
.db-task-runs-list {
  padding: 20px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.task-info {
  flex: 1;
}

.task-name {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 8px 0;
  color: #333;
}

.task-desc {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.header-right {
  display: flex;
  gap: 8px;
}

.runs-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.run-card {
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s;
}

.run-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px 0 rgba(64, 158, 255, 0.1);
}

.run-card.active {
  border-color: #409eff;
  background: #f0f9ff;
}

.run-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  gap: 12px;
}

.run-main {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.run-title {
  font-weight: 600;
  color: #333;
  font-size: 16px;
}

.run-times {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: #999;
  white-space: nowrap;
  margin-left: 12px;
}

.run-chevron {
  margin-left: 12px;
  font-size: 18px;
  color: #999;
  transition: transform 0.3s;
}

.run-chevron.expanded {
  transform: rotate(180deg);
}

.run-content {
  border-top: 1px solid #ebeef5;
  background: #fafafa;
}

.tabs-wrapper {
  padding: 0;
}

.tabs-wrapper :deep(.el-tabs__content) {
  padding: 16px;
}

.loading-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 32px;
  color: #666;
}

.loading-wrapper .is-loading {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.empty-tip {
  text-align: center;
  padding: 32px;
  color: #999;
}

.logs-list,
.contexts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.log-item,
.context-item {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.log-script,
.context-script {
  background: #f5f7fa;
  padding: 8px 12px;
  font-family: monospace;
  font-size: 13px;
  font-weight: 600;
  color: #333;
}

.log-output,
.context-data {
  background: #f9f9f9;
  padding: 12px;
  margin: 0;
  max-height: 400px;
  overflow: auto;
  font-family: monospace;
  font-size: 13px;
  color: #666;
  white-space: pre-wrap;
  word-break: break-all;
}

@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
  }

  .header-left {
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
  }

  .run-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .run-times {
    width: 100%;
    flex-direction: row;
    gap: 8px;
  }

  .log-output,
  .context-data {
    max-height: 250px;
    font-size: 12px;
  }
}
</style>
