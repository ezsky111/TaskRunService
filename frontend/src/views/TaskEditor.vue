<template>
  <div class="task-editor">
    <div class="header">
      <h2>{{ isNew ? '新建任务' : '编辑任务' }}</h2>
    </div>
    
    <div class="form">
      <div class="form-group">
        <label>任务ID:</label>
        <input v-model="form.task_id" :disabled="!isNew" type="text" placeholder="输入任务ID">
      </div>
      
      <div class="form-group">
        <label>任务代码:</label>
        <textarea v-model="form.content" placeholder="输入Python代码" rows="20"></textarea>
      </div>
      
      <div class="form-actions">
        <button @click="saveTast" class="btn btn-primary">保存</button>
        <button @click="$router.back()" class="btn btn-secondary">返回</button>
      </div>
    </div>
  </div>
</template>

<script>
import { taskApi } from '../api/index.js'

export default {
  name: 'TaskEditor',
  data() {
    return {
      form: {
        task_id: '',
        content: ''
      },
      isNew: true
    }
  },
  methods: {
    async loadTask() {
      const taskId = this.$route.params.id
      if (taskId) {
        this.isNew = false
        try {
          const res = await taskApi.getTask(taskId)
          this.form = res.data.data
        } catch (error) {
          alert('加载任务失败: ' + error.message)
        }
      }
    },
    async saveTast() {
      if (!this.form.task_id) {
        alert('请输入任务ID')
        return
      }
      
      try {
        if (this.isNew) {
          await taskApi.createTask(this.form)
          alert('任务创建成功')
        } else {
          await taskApi.updateTask(this.form.task_id, this.form)
          alert('任务更新成功')
        }
        this.$router.back()
      } catch (error) {
        alert('保存失败: ' + error.response?.data?.message || error.message)
      }
    }
  },
  mounted() {
    this.loadTask()
  }
}
</script>

<style scoped>
.task-editor {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header h2 {
  font-size: 1.5rem;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.form-group textarea {
  resize: vertical;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s;
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
</style>
