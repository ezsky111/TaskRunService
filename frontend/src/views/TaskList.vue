<template>
  <div class="task-list">
    <div class="header">
      <h2>编排任务</h2>
      <router-link to="/dbtasks/new" class="btn btn-primary">+ 新建编排任务</router-link>
    </div>
    
    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else-if="tasks.length === 0" class="empty">
      <p>暂无编排任务，<router-link to="/dbtasks/new">创建新任务</router-link></p>
    </div>
    
    <div v-else class="tasks-grid">
      <div v-for="task in tasks" :key="task.id" class="task-card">
        <div class="task-header">
          <h3>{{ task.name }}</h3>
          <span class="task-id">ID: {{ task.id }}</span>
        </div>
        <div class="task-info">
          <p>{{ task.description || '无描述' }}</p>
          <p class="scripts-info">脚本数: {{ task.scripts.length }}</p>
        </div>
        <div class="task-actions">
          <router-link :to="`/dbtasks/${task.id}/runs`" class="btn btn-small btn-info">查看运行</router-link>
          <router-link :to="`/dbtasks/${task.id}/execute`" class="btn btn-small btn-success">执行</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { dbTaskApi } from '../api/index.js'

export default {
  name: 'TaskList',
  data() {
    return {
      tasks: [],
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
        alert('加载任务列表失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    formatDate(dateStr) {
      return new Date(dateStr).toLocaleString('zh-CN')
    }
  },
  mounted() {
    this.loadTasks()
    // 每 5 秒刷新一次
    this.timer = setInterval(() => {
      this.loadTasks()
    }, 5000)
  },
  beforeUnmount() {
    if (this.timer) {
      clearInterval(this.timer)
    }
  }
}
</script>

<style scoped>
.task-list {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header h2 {
  font-size: 1.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-info {
  background: #17a2b8;
  color: white;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-small {
  padding: 0.25rem 0.75rem;
  font-size: 0.8rem;
}

.loading, .empty {
  text-align: center;
  padding: 2rem;
  color: #999;
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.task-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1.5rem;
  background: #fafafa;
  transition: all 0.3s;
}

.task-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  border-bottom: 2px solid #667eea;
  padding-bottom: 0.5rem;
}

.task-header h3 {
  margin: 0;
  color: #333;
}

.task-id {
  font-size: 0.8rem;
  color: #999;
  background: #e9ecef;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
}

.task-info {
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.task-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.active-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid #ddd;
}

.active-tasks {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.active-task {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f0f7ff;
  border-left: 4px solid #667eea;
  border-radius: 4px;
}

.status {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.status.running {
  background: #cfe2ff;
  color: #084298;
}

.status.success {
  background: #d1e7dd;
  color: #0f5132;
}

.status.failed {
  background: #f8d7da;
  color: #842029;
}
</style>
