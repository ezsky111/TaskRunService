<template>
  <div class="task-logs">
    <div class="header">
      <h2>编排任务日志</h2>
      <button @click="loadTasks" class="btn btn-primary">刷新</button>
    </div>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else class="logs-container">
      <div class="task-selector">
        <label>选择任务:</label>
        <select v-model="selectedTaskId" @change="loadRuns" class="task-select">
          <option value="">-- 选择任务 --</option>
          <option v-for="task in tasks" :key="task.id" :value="task.id">
            {{ task.name }} (ID: {{ task.id }})
          </option>
        </select>
      </div>
      
      <div v-if="selectedTaskId" class="runs-section">
        <h3>运行记录</h3>
        <div v-if="runs.length === 0" class="empty">暂无运行记录</div>
        <div v-else class="runs-list">
          <div v-for="run in runs" :key="run.run_id" class="run-item" @click="viewRunLogs(run.run_id)">
            <span>运行ID: {{ run.run_id }}</span>
            <span class="status" :class="run.status">{{ run.status }}</span>
            <span>开始: {{ formatDate(run.started_at) }}</span>
            <span v-if="run.finished_at">结束: {{ formatDate(run.finished_at) }}</span>
          </div>
        </div>
      </div>
      
      <div v-if="currentLogs.length > 0" class="logs-section">
        <h3>执行日志</h3>
        <div v-for="log in currentLogs" :key="log.script" class="log-block">
          <div class="log-header">{{ log.script }}</div>
          <pre class="log-content">{{ log.output }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { dbTaskApi } from '../api/index.js'

export default {
  name: 'TaskLogs',
  data() {
    return {
      tasks: [],
      runs: [],
      currentLogs: [],
      selectedTaskId: '',
      loading: true
    }
  },
  methods: {
    async loadTasks() {
      try {
        this.loading = true
        const res = await this.$http.get('/tasks/db')
        this.tasks = res.data.data || []
      } catch (error) {
        console.error('加载任务列表失败:', error)
      } finally {
        this.loading = false
      }
    },
    async loadRuns() {
      if (!this.selectedTaskId) {
        this.runs = []
        this.currentLogs = []
        return
      }
      try {
        const res = await dbTaskApi.getTaskRuns(this.selectedTaskId)
        this.runs = res.data.data || []
        this.currentLogs = []
      } catch (error) {
        console.error('加载运行记录失败:', error)
      }
    },
    async viewRunLogs(runId) {
      try {
        const res = await dbTaskApi.getRunLogs(runId)
        this.currentLogs = res.data.data || []
      } catch (error) {
        console.error('加载日志失败:', error)
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleString('zh-CN')
    }
  },
  mounted() {
    this.loadTasks()
  }
}
</script>

<style scoped>
.task-logs { background: white; border-radius: 8px; padding: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.header h2 { font-size: 1.5rem; }
.loading, .empty { text-align: center; padding: 2rem; color: #999; }
.logs-container { }
.task-selector { margin-bottom: 2rem; }
.task-selector label { display: block; margin-bottom: 0.5rem; font-weight: 600; }
.task-select { padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; width: 100%; max-width: 400px; }
.runs-section, .logs-section { margin-bottom: 2rem; }
.runs-section h3, .logs-section h3 { margin-bottom: 1rem; font-size: 1.1rem; }
.runs-list { }
.run-item { display: flex; gap: 2rem; align-items: center; padding: 1rem; margin-bottom: 0.75rem; background: #f5f5f5; border-radius: 4px; cursor: pointer; transition: background 0.3s; }
.run-item:hover { background: #efefef; }
.status { padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }
.status.success { background: #d1e7dd; color: #0f5132; }
.status.failed, .status.error, .status.timeout { background: #f8d7da; color: #842029; }
.status.running { background: #cfe2ff; color: #084298; }
.log-block { margin-bottom: 1.5rem; border: 1px solid #ddd; border-radius: 4px; overflow: hidden; }
.log-header { background: #f5f5f5; padding: 0.75rem; font-weight: 600; border-bottom: 1px solid #ddd; }
.log-content { background: #1e1e1e; color: #d4d4d4; font-family: 'Courier New', monospace; font-size: 0.85rem; padding: 1rem; margin: 0; max-height: 400px; overflow: auto; }
.btn { padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; transition: all 0.3s; }
.btn-primary { background: #667eea; color: white; }
.btn-small { padding: 0.25rem 0.75rem; font-size: 0.8rem; }
</style>
