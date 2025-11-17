<template>
  <div class="db-task-runs">
    <div class="header">
      <h2>任务运行历史</h2>
      <button @click="loadRuns" class="btn btn-primary" :disabled="loading">
        <span v-if="loading" class="spinner"></span>
        {{ loading ? '加载中...' : '刷新' }}
      </button>
    </div>

    <div v-if="loading && runs.length === 0" class="loading-state">
      <div class="spinner-large"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="runs.length === 0" class="empty-state">
      <p>暂无运行记录</p>
    </div>

    <div v-else class="runs-list">
      <div v-for="run in runs" :key="run.run_id" class="run-item" :class="{ expanded: selectedRunId === run.run_id }">
        <div class="run-header" @click="toggleRun(run.run_id)">
          <div class="run-info">
            <span class="run-id">运行 #{{ run.run_id }}</span>
            <span class="status" :class="`status-${run.status}`">{{ run.status }}</span>
            <span class="time">{{ formatDate(run.started_at) }}</span>
          </div>
          <span class="expand-icon">{{ selectedRunId === run.run_id ? '▼' : '▶' }}</span>
        </div>

        <div v-if="selectedRunId === run.run_id" class="run-expand">
          <div v-if="currentLoading" class="loading-content">
            <div class="spinner"></div>
            加载日志中...
          </div>
          <template v-else>
            <div class="logs-tabs">
              <button 
                v-for="tab in ['logs', 'contexts']" 
                :key="tab"
                :class="['tab', { active: activeTab === tab }]"
                @click.stop="activeTab = tab"
              >
                {{ tab === 'logs' ? '执行日志' : '环境变量' }}
              </button>
            </div>
            
            <div v-if="activeTab === 'logs'" class="logs-section">
              <div v-if="logs.length === 0" class="no-data">暂无日志</div>
              <div v-for="log in logs" :key="log.script" class="log-block">
                <div class="log-header">{{ log.script }}</div>
                <pre class="log-content">{{ log.output }}</pre>
              </div>
            </div>

            <div v-if="activeTab === 'contexts'" class="contexts-section">
              <div v-if="contexts.length === 0" class="no-data">暂无环境变量</div>
              <div v-for="ctx in contexts" :key="ctx.script" class="context-block">
                <div class="context-header">{{ ctx.script }}</div>
                <pre class="context-content">{{ JSON.stringify(ctx.context, null, 2) }}</pre>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { dbTaskApi } from '../api/index.js'

export default {
  name: 'DbTaskRuns',
  props: {
    taskId: [String, Number]
  },
  data() {
    return {
      runs: [],
      logs: [],
      contexts: [],
      selectedRunId: null,
      loading: false,
      currentLoading: false,
      activeTab: 'logs'
    }
  },
  methods: {
    toggleRun(runId) {
      if (this.selectedRunId === runId) {
        this.selectedRunId = null
      } else {
        this.viewLogs(runId)
      }
    },
    async loadRuns() {
      this.loading = true
      try {
        const res = await dbTaskApi.getTaskRuns(Number(this.taskId))
        if (res.data.success) {
          this.runs = res.data.data || []
          this.$root.$notify?.success('加载成功')
        } else {
          this.$root.$notify?.error(res.data.message || '加载失败')
        }
      } catch (error) {
        this.$root.$notify?.error('加载运行记录失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    async viewLogs(runId) {
      this.selectedRunId = runId
      this.currentLoading = true
      this.activeTab = 'logs'
      try {
        const [logsRes, contextsRes] = await Promise.all([
          dbTaskApi.getRunLogs(runId),
          dbTaskApi.getRunContexts(runId)
        ])
        
        if (logsRes.data.success) {
          this.logs = logsRes.data.data || []
        }
        if (contextsRes.data.success) {
          this.contexts = contextsRes.data.data || []
        }
      } catch (error) {
        this.$root.$notify?.error('加载日志失败: ' + error.message)
      } finally {
        this.currentLoading = false
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleString('zh-CN')
    }
  },
  mounted() {
    this.loadRuns()
  }
}
</script>

<style scoped>
.db-task-runs {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 1rem;
}

.header h2 {
  font-size: 1.5rem;
  margin: 0;
  color: #333;
  font-weight: 600;
}

.loading-state,
.empty-state,
.no-data {
  text-align: center;
  padding: 2rem;
  color: #999;
}

.spinner-large {
  width: 50px;
  height: 50px;
  border: 4px solid #f0f0f0;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid #f0f0f0;
  border-top: 2px solid #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-right: 0.5rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.runs-list {
  space-y: 1rem;
}

.run-item {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  margin-bottom: 1rem;
  overflow: hidden;
  transition: all 0.3s;
  background: #fafafa;
}

.run-item:hover {
  border-color: #667eea;
  background: #f5f7ff;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.run-item.expanded {
  background: white;
  border-color: #667eea;
  box-shadow: 0 2px 12px rgba(102, 126, 234, 0.15);
}

.run-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  cursor: pointer;
  user-select: none;
}

.run-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.run-id {
  font-weight: 600;
  color: #333;
  min-width: 80px;
}

.status {
  padding: 0.3rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
}

.status-success {
  background: #d4edda;
  color: #155724;
}

.status-failed,
.status-error,
.status-timeout {
  background: #f8d7da;
  color: #721c24;
}

.status-running {
  background: #cfe2ff;
  color: #084298;
}

.time {
  color: #999;
  font-size: 0.9rem;
}

.expand-icon {
  color: #667eea;
  font-size: 0.8rem;
  transition: transform 0.3s;
}

.run-expand {
  border-top: 1px solid #f0f0f0;
  padding: 1rem;
  background: #f9fafb;
}

.loading-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  color: #667eea;
  justify-content: center;
}

.logs-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  border-bottom: 2px solid #f0f0f0;
}

.tab {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
  font-weight: 600;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
  font-size: 0.95rem;
}

.tab:hover {
  color: #667eea;
}

.tab.active {
  color: #667eea;
  border-bottom-color: #667eea;
}

.logs-section,
.contexts-section {
  space-y: 1rem;
}

.log-block,
.context-block {
  margin-bottom: 1rem;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  overflow: hidden;
}

.log-header,
.context-header {
  background: #f5f5f5;
  padding: 0.75rem 1rem;
  font-weight: 600;
  border-bottom: 1px solid #e8e8e8;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.context-header {
  background: #e8f4f8;
  color: #0c5aa0;
}

.log-content,
.context-content {
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  padding: 1rem;
  margin: 0;
  max-height: 400px;
  overflow: auto;
  background: #1e1e1e;
  color: #d4d4d4;
  line-height: 1.5;
}

.context-content {
  background: #f5f5f5;
  color: #333;
}

.log-content::-webkit-scrollbar,
.context-content::-webkit-scrollbar {
  width: 8px;
}

.log-content::-webkit-scrollbar-track,
.context-content::-webkit-scrollbar-track {
  background: #f0f0f0;
}

.log-content::-webkit-scrollbar-thumb,
.context-content::-webkit-scrollbar-thumb {
  background: #999;
  border-radius: 4px;
}

.log-content::-webkit-scrollbar-thumb:hover,
.context-content::-webkit-scrollbar-thumb:hover {
  background: #666;
}
</style>
