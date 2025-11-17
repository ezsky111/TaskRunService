<template>
  <div class="db-task-execute">
    <div class="header">
      <h2>执行任务</h2>
    </div>
    <div class="form">
      <div class="form-group">
        <label>环境变量（JSON格式）:</label>
        <textarea v-model="contextStr" rows="5" placeholder='{"key": "value"}'></textarea>
      </div>
      <div class="form-actions">
        <button @click="executeTask" class="btn btn-primary">执行</button>
        <button @click="$router.back()" class="btn btn-secondary">返回</button>
      </div>
    </div>
    <div v-if="runId" class="result">
      <p>任务已提交，运行ID: {{ runId }}</p>
    </div>
  </div>
</template>

<script>
import { dbTaskApi } from '../api/index.js'

export default {
  name: 'DbTaskExecute',
  props: {
    taskId: [String, Number]
  },
  data() {
    return {
      contextStr: '',
      runId: null
    }
  },
  methods: {
    async executeTask() {
      let context = {}
      if (this.contextStr.trim()) {
        try {
          context = JSON.parse(this.contextStr)
        } catch (e) {
          alert('环境变量格式错误，应为JSON')
          return
        }
      }
      try {
        const res = await dbTaskApi.executeTask(Number(this.taskId), context)
        this.runId = res.data.run_id
        alert('任务已提交: ' + this.runId)
      } catch (error) {
        alert('执行失败: ' + error.response?.data?.message || error.message)
      }
    }
  }
}
</script>

<style scoped>
.db-task-execute { background: white; border-radius: 8px; padding: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.header h2 { font-size: 1.5rem; margin-bottom: 2rem; }
.form-group { margin-bottom: 1.5rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; color: #333; }
.form-group textarea { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem; resize: vertical; }
.form-actions { display: flex; gap: 1rem; margin-top: 2rem; }
.btn { padding: 0.75rem 1.5rem; border: none; border-radius: 4px; cursor: pointer; font-size: 1rem; transition: all 0.3s; }
.btn-primary { background: #667eea; color: white; }
.btn-primary:hover { background: #5568d3; }
.btn-secondary { background: #6c757d; color: white; }
.result { margin-top: 2rem; color: #3182ce; font-weight: 600; }
</style>
