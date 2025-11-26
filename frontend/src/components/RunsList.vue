<template>
  <div class="space-y-4 runs-list">
    <!-- 头部：返回按钮 + 任务信息 -->
    <div class="flex items-center justify-between mb-6 run-header">
      <div class="run-header-left flex items-center gap-4">
        <button
          v-if="showBackButton"
          @click="$emit('back')"
          class="inline-flex items-center gap-2 rounded-lg bg-slate-200 px-4 py-2 font-semibold text-slate-900 transition hover:bg-slate-300 run-back-btn"
        >
          <ChevronLeft :size="18" />
          返回
        </button>
        <div v-if="taskInfo" class="run-task-info">
          <h2 class="text-2xl font-bold text-slate-900">{{ taskInfo.name }}</h2>
          <p class="text-sm text-slate-600">{{ taskInfo.description || '暂无描述' }}</p>
        </div>
      </div>
      <div class="run-header-right">
        <button
          @click="handleRefresh"
          :disabled="loading"
          class="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white shadow-md transition hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed run-refresh-btn"
        >
          <RefreshCw v-if="!loading" :size="18" />
          <Loader v-else :size="18" class="animate-spin" />
          {{ loading ? '刷新中...' : '刷新' }}
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && runs.length === 0" class="flex flex-col items-center justify-center rounded-lg bg-white p-12 shadow-sm">
      <Loader class="mb-4 animate-spin text-blue-600" :size="32" />
      <p class="text-slate-600">加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="runs.length === 0" class="flex flex-col items-center justify-center rounded-lg bg-white p-12 shadow-sm">
      <History class="mb-4 text-slate-400" :size="32" />
      <p class="text-slate-600">暂无运行记录</p>
    </div>

    <!-- 运行列表 -->
    <div v-else class="space-y-2">
      <div
        v-for="run in runs"
        :key="run.run_id"
        class="overflow-hidden rounded-lg border border-slate-200 bg-white transition hover:border-blue-400 hover:shadow-md run-card"
        :class="{ 'border-blue-600 bg-blue-50 shadow-md': selectedRunId === run.run_id }"
      >
        <!-- 运行头部（可点击展开） -->
        <button
          @click="toggleRun(run.run_id)"
          class="w-full px-6 py-4 text-left transition run-toggle-btn"
          :class="{ 'bg-blue-50': selectedRunId === run.run_id }"
          aria-expanded="{ selectedRunId === run.run_id }"
        >
          <div class="flex items-center justify-between run-header-row">
            <div class="flex flex-1 items-center gap-4 run-main">
              <span class="font-semibold text-slate-900 run-title">运行 #{{ run.run_id }}</span>
              <Badge :variant="statusVariant(run.status)">{{ run.status }}</Badge>
            </div>

            <div class="run-times text-sm text-slate-500">
              <span class="run-start">{{ formatDate(run.started_at) }}</span>
              <span v-if="run.finished_at" class="run-end">结束: {{ formatDate(run.finished_at) }}</span>
            </div>

            <ChevronDown
              :size="20"
              class="text-slate-600 transition run-chevron"
              :class="{ 'rotate-180': selectedRunId === run.run_id }"
            />
          </div>
        </button>

        <!-- 运行展开内容 -->
        <div
          v-if="selectedRunId === run.run_id"
          class="border-t border-slate-200 bg-slate-50"
        >
          <!-- 选项卡 -->
          <div class="flex gap-2 border-b border-slate-200 px-6 py-3 tabs-wrapper">
            <button
              v-for="tab in ['logs', 'contexts']"
              :key="tab"
              @click="activeTab = tab"
              class="rounded-t-lg px-4 py-2 font-semibold transition tab-btn"
              :class="activeTab === tab ? 'active' : ''"
            >
              {{ tab === 'logs' ? '执行日志' : '环境变量' }}
            </button>
          </div>

          <!-- 内容区域 -->
          <div class="px-6 py-4">
            <!-- 日志加载中 -->
            <div v-if="currentRunLoading" class="flex items-center justify-center gap-2 py-8 text-slate-600">
              <Loader :size="18" class="animate-spin" />
              加载日志中...
            </div>

            <!-- 执行日志标签 -->
            <template v-else-if="activeTab === 'logs'">
              <div v-if="currentLogs.length === 0" class="py-8 text-center text-slate-600">
                暂无日志
              </div>
              <div v-else class="space-y-3">
                <div v-for="log in currentLogs" :key="log.script" class="overflow-hidden rounded-lg border border-slate-200">
                  <div class="bg-slate-100 px-4 py-2 font-mono text-sm font-semibold text-slate-700">
                    {{ log.script }}
                  </div>
                  <pre  class="overflow-auto bg-slate-900 p-4 text-sm text-slate-300 font-mono run-pre">{{ log.output }}</pre>
                </div>
              </div>
            </template>

            <!-- 环境变量标签 -->
            <template v-else-if="activeTab === 'contexts'">
              <div v-if="currentContexts.length === 0" class="py-8 text-center text-slate-600">
                暂无环境变量
              </div>
              <div v-else class="space-y-3">
                <div v-for="ctx in currentContexts" :key="ctx.script" class="overflow-hidden rounded-lg border border-slate-200">
                  <div class="bg-blue-50 px-4 py-2 font-mono text-sm font-semibold text-blue-700">
                    {{ ctx.script }}
                  </div>
                  <pre class="overflow-auto bg-slate-50 p-4 text-sm text-slate-900 font-mono run-pre">{{ JSON.stringify(ctx.context, null, 2) }}</pre>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ChevronLeft, ChevronDown, RefreshCw, Loader, History } from 'lucide-vue-next'
import { Badge } from '@/components/ui'

export default {
  name: 'RunsList',
  components: {
    ChevronLeft,
    ChevronDown,
    RefreshCw,
    Loader,
    History,
    Badge
  },
  props: {
    runs: {
      type: Array,
      default: () => []
    },
    taskInfo: {
      type: Object,
      default: null
    },
    loading: Boolean,
    showBackButton: {
      type: Boolean,
      default: true
    }
  },
  emits: ['back', 'refresh', 'view-logs'],
  data() {
    return {
      selectedRunId: null,
      currentRunLoading: false,
      activeTab: 'logs',
      currentLogs: [],
      currentContexts: []
    }
  },
  watch: {
    runs() {
      this.selectedRunId = null
      this.currentLogs = []
      this.currentContexts = []
    }
  },
  methods: {
    async toggleRun(runId) {
      if (this.selectedRunId === runId) {
        this.selectedRunId = null
      } else {
        await this.loadRunDetails(runId)
      }
    },
    async loadRunDetails(runId) {
      this.selectedRunId = runId
      this.currentRunLoading = true
      this.activeTab = 'logs'
      this.$emit('view-logs', runId, (logs, contexts) => {
        this.currentLogs = logs || []
        this.currentContexts = contexts || []
        this.currentRunLoading = false
      })
    },
    handleRefresh() {
      this.$emit('refresh')
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleString('zh-CN')
    },
    statusVariant(status) {
      const variants = {
        success: 'green',
        failed: 'red',
        error: 'red',
        timeout: 'red',
        running: 'blue'
      }
      return variants[status] || 'slate'
    }
  }
}
</script>

<style scoped>
/* RunsList mobile optimizations */
.runs-list {}
.run-header { align-items: flex-start; }
.run-back-btn { min-width: 86px }
.run-refresh-btn { min-width: 86px }

.run-card { overflow: hidden; margin-bottom: 14px; }
.run-card:last-child { margin-bottom: 0; }
.run-header-row { gap: 12px }
.run-main .run-title { font-weight: 700 }
.run-times { white-space: nowrap; margin-left: 12px }
.run-chevron { margin-left: 12px }
.tabs-wrapper { overflow:auto }
.tab-btn { color: #475569 }
.tab-btn.active { border-bottom: 2px solid #2563eb; color: #2563eb }
.run-pre { max-height: 520px; white-space: pre; }

@media (max-width: 768px) {
  .run-header { flex-direction: column; gap: 8px }
  .run-header-left { width: 100%; display:flex; align-items:center; gap:12px }
  .run-header-right { width: 100%; display:flex; justify-content:flex-end }
  .run-task-info { flex:1 }
  pre{
  width:290px
}
  .run-card { margin: 0 0 14px 0; }
  .run-card:last-child { margin-bottom: 0 }
  .run-header-row { display:flex; flex-direction:column; align-items:flex-start; gap:8px }
  .run-main { width:100%; gap:8px }
  .run-times { order:3; color:#64748b }
  .run-chevron { order:2; align-self:flex-end }

  .tabs-wrapper { flex-direction:row; gap:8px; overflow:auto }
  .tab-btn { flex: 1 0 auto; min-width: 120px; text-align:center }

  .run-pre { max-height: 240px; font-size: 13px }
  .run-toggle-btn { padding: 12px }
}
</style>
