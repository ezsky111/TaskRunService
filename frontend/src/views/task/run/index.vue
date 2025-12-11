<template>
  <div class="task-runs-page art-full-height">
    <!-- 搜索和操作栏 -->
    <div style="margin-bottom: 12px">
      <el-space>
        <el-input
          v-model="searchTaskId"
          placeholder="按任务ID筛选"
          style="width: 200px"
          clearable
          @input="handleSearch"
        />
        <el-button @click="loadRuns" :loading="loading">刷新</el-button>
      </el-space>
    </div>

    <!-- 表格卡片 -->
    <el-card class="art-table-card" shadow="never">
      <el-table
        :data="filteredRuns"
        :loading="loading"
        stripe
        @row-click="handleRowClick"
        style="cursor: pointer"
      >
        <el-table-column prop="run_id" label="运行ID" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status) as any">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="started_at" label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.started_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="finished_at" label="结束时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.finished_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 执行详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="执行详情" width="800px" :destroy-on-close="true">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="执行日志" name="logs">
          <div v-if="detailLoading" class="loading-wrapper">
            <el-icon class="is-loading"><Loading /></el-icon>
            加载中...
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
          <div v-if="detailLoading" class="loading-wrapper">
            <el-icon class="is-loading"><Loading /></el-icon>
            加载中...
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
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { fetchGetAllDbTaskRuns,fetchGetDbTaskRuns,fetchGetDbRunLogs,fetchGetDbRunContexts } from '@/api/task-db'

interface Run {
  run_id: string | number
  status: string
  started_at: string
  finished_at?: string
}

interface LogItem {
  script: string
  output: string
}

interface ContextItem {
  script: string
  context: Record<string, any>
}

const route = useRoute()

const taskId = computed(() => route.query.taskId ? Number(route.query.taskId) : null)

const runs = ref<Run[]>([])
const loading = ref(false)
const detailLoading = ref(false)
const detailDialogVisible = ref(false)
const activeTab = ref('logs')
const currentLogs = ref<LogItem[]>([])
const currentContexts = ref<ContextItem[]>([])
const selectedRunId = ref<string | number | null>(null)
const searchTaskId = ref('')

const filteredRuns = computed(() => {
  if (!searchTaskId.value) {
    return runs.value
  }
  return runs.value.filter(run => String(run.run_id).includes(searchTaskId.value))
})

const loadRuns = async () => {
  loading.value = true
  runs.value = [] // 清空前一次的数据
  try {
    let res: any
    // 如果有 taskId，按任务ID加载；否则加载所有运行记录
    if (taskId.value) {
      res = await fetchGetDbTaskRuns(taskId.value)
    } else {
      // 尝试调用通用的获取所有运行接口，如果不存在则使用第一个任务的运行记录作为示例
      try {
        res = await fetchGetAllDbTaskRuns().then(r => r.json())
      } catch (e) {
        // 如果接口不存在，返回空列表
        res = { success: true, data: [] }
      }
    }
    runs.value = res
  } catch (error: any) {
    ElMessage.error('加载运行记录失败: ' + (error.message || ''))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // 搜索是实时过滤的，无需额外操作
}

const handleRowClick = (row: Run) => {
  selectedRunId.value = row.run_id
  activeTab.value = 'logs'
  detailDialogVisible.value = true
  loadRunDetails(row.run_id)
}

const loadRunDetails = async (runId: string | number) => {
  detailLoading.value = true
  try {
    const [logsRes, contextsRes] = await Promise.all([
      fetchGetDbRunLogs(runId),
      fetchGetDbRunContexts(runId)
    ])
    currentLogs.value = logsRes || []
    currentContexts.value = contextsRes || []
  } catch (error: any) {
    ElMessage.error('加载详情失败: ' + (error.message || ''))
  } finally {
    detailLoading.value = false
  }
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const statusType = (status: string) => {
  const typeMap: Record<string, string> = {
    success: 'success',
    failed: 'danger',
    error: 'danger',
    timeout: 'danger',
    running: 'warning'
  }
  return typeMap[status] || 'info'
}

onMounted(() => {
  loadRuns()
})

watch(() => route.query, () => {
  loadRuns()
}, { deep: true })
</script>

<style scoped>
.task-runs-page {
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
</style>
