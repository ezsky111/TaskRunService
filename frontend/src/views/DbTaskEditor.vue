<template>
  <div class="db-task-editor">
    <div class="header">
      <h2>新建编排任务</h2>
      <button v-if="inline" class="close-icon" @click="$emit('close')">
        <X :size="18" />
      </button>
    </div>
    <div class="form">
      <div class="form-group">
        <label>任务名称:</label>
        <input v-model="form.name" type="text" placeholder="输入任务名称">
      </div>
      <div class="form-group">
        <label>任务描述:</label>
        <input v-model="form.description" type="text" placeholder="输入描述">
      </div>
      <div class="form-group">
        <label>选择脚本并编排顺序:</label>
        <div class="scripts-list">
          <div
            v-for="(script, idx) in form.scripts"
            :key="script + '_' + idx"
            class="script-item draggable"
            draggable="true"
            @dragstart="dragStart($event, idx)"
            @dragover.prevent
            @drop="onDrop($event, idx)"
          >
            <div class="script-left">
              <span class="drag-handle" title="拖拽移动">⋮⋮</span>
              <span class="script-name">{{ script }}</span>
            </div>
            <div class="script-actions">
              <button @click="moveUp(idx)" :disabled="idx === 0" class="btn btn-small">↑</button>
              <button @click="moveDown(idx)" :disabled="idx === form.scripts.length - 1" class="btn btn-small">↓</button>
              <button @click="removeScript(idx)" class="btn btn-small btn-danger">移除</button>
            </div>
          </div>
        </div>
        <div class="available-scripts">
          <div class="available-title">可用脚本:</div>
          <div class="available-grid">
            <div v-for="script in availableScripts" :key="script" class="available-card">
              <div class="card-name">{{ script }}</div>
              <button @click="addScript(script)" class="btn btn-info btn-small">添加</button>
            </div>
          </div>
        </div>
      </div>
      <div class="form-actions">
        <button @click="saveTask" class="btn btn-primary" :disabled="saving">
          <span v-if="saving" class="spinner"></span>
          {{ saving ? '保存中...' : '保存' }}
        </button>
        <button @click="inline ? $emit('close') : $router.back()" class="btn btn-secondary" :disabled="saving">返回</button>
      </div>
    </div>
  </div>
</template>

<script>
import { dbTaskApi } from '../api/index.js'
import { X } from 'lucide-vue-next'

export default {
  name: 'DbTaskEditor',
  components: { X },
  props: {
    inline: { type: Boolean, default: false },
    task: { type: Object, default: null }
  },
  data() {
    return {
      form: {
        name: '',
        description: '',
        scripts: []
      },
      availableScripts: [],
      saving: false
      ,dragIndex: null
    }
  },
  methods: {
    populateFromTask() {
      if (this.task) {
        this.form.name = this.task.name || ''
        this.form.description = this.task.description || ''
        this.form.scripts = Array.isArray(this.task.scripts) ? [...this.task.scripts] : []
      }
    },
    async loadScripts() {
      try {
        const res = await this.$http.get('/tasks')
        this.availableScripts = res.data.data.map(t => t.name + '.py')
      } catch (error) {
        this.$root.$notify?.error('加载脚本列表失败: ' + error.message)
      }
    },
    addScript(script) {
      if (!this.form.scripts.includes(script)) {
        this.form.scripts.push(script)
        this.$root.$notify?.info('已添加脚本: ' + script)
      }
    },
    dragStart(e, idx) {
      this.dragIndex = idx
      try { e.dataTransfer.setData('text/plain', String(idx)) } catch (e) {}
    },
    onDrop(e, idx) {
      const from = this.dragIndex != null ? this.dragIndex : Number(e.dataTransfer.getData('text/plain'))
      if (isNaN(from)) return
      const item = this.form.scripts.splice(from, 1)[0]
      // if dropping after removal affects target index
      const to = from < idx ? idx : idx
      this.form.scripts.splice(to, 0, item)
      this.dragIndex = null
    },
    removeScript(idx) {
      const script = this.form.scripts[idx]
      this.form.scripts.splice(idx, 1)
      this.$root.$notify?.info('已移除脚本: ' + script)
    },
    moveUp(idx) {
      if (idx > 0) {
        [this.form.scripts[idx - 1], this.form.scripts[idx]] = [this.form.scripts[idx], this.form.scripts[idx - 1]]
      }
    },
    moveDown(idx) {
      if (idx < this.form.scripts.length - 1) {
        [this.form.scripts[idx], this.form.scripts[idx + 1]] = [this.form.scripts[idx + 1], this.form.scripts[idx]]
      }
    },
    async saveTask() {
      if (!this.form.name) {
        this.$root.$notify?.warning('请填写任务名称')
        return
      }
      if (this.form.scripts.length === 0) {
        this.$root.$notify?.warning('请选择至少一个脚本')
        return
      }
      
      this.saving = true
      try {
        if (this.task && this.task.id) {
          // 编辑已有 db task
          const res = await dbTaskApi.updateTask(this.task.id, {
            name: this.form.name,
            description: this.form.description,
            scripts: this.form.scripts
          })
          this.$root.$notify?.success(res.data.message || '更新成功')
          if (this.inline) this.$emit('updated', this.task.id)
        } else {
          const res = await dbTaskApi.createTask({
            name: this.form.name,
            description: this.form.description,
            scripts: this.form.scripts
          })
          this.$root.$notify?.success('任务创建成功，ID: ' + res.data.task_id)
          if (this.inline) this.$emit('created', res.data.task_id)
          else setTimeout(() => this.$router.back(), 1500)
        }
      } catch (error) {
        this.$root.$notify?.error('保存失败: ' + (error.response?.data?.message || error.message))
      } finally {
        this.saving = false
      }
    }
  },
  watch: {
    task: {
      handler() { this.populateFromTask() },
      immediate: true
    }
  },
  mounted() {
    this.loadScripts()
    this.populateFromTask()
  }
}
</script>

<style scoped>
.db-task-editor { 
  background: white; 
  border-radius: 12px; 
  padding: 2rem; 
  box-shadow: 0 2px 12px rgba(0,0,0,0.08); 
}

.header h2 { 
  font-size: 1.5rem; 
  margin-bottom: 2rem; 
  color: #333;
  font-weight: 600;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 1rem;
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

.form-group input { 
  width: 100%; 
  padding: 0.75rem; 
  border: 1px solid #ddd; 
  border-radius: 6px; 
  font-size: 0.9rem;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.scripts-list { 
  background: #f5f5f5; 
  border-radius: 6px; 
  padding: 1rem; 
  margin-bottom: 1rem; 
}

.script-item { 
  display: flex; 
  align-items: center; 
  justify-content: space-between; 
  gap: 1rem; 
  margin-bottom: 0.75rem; 
  background: white; 
  padding: 0.75rem; 
  border-radius: 6px; 
  border: 1px solid #ddd;
  transition: all 0.3s;
}

.script-item:hover {
  border-color: #667eea;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.1);
}

.script-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.drag-handle {
  cursor: grab;
  color: #9aa4b2;
  font-size: 1.1rem;
  user-select: none;
}

.available-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.75rem;
}

.available-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border: 1px solid #e6e9ee;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
}

.card-name {
  font-size: 0.9rem;
  color: #2d3748;
}

.script-name { 
  flex: 1;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.script-actions { 
  display: flex; 
  gap: 0.5rem; 
}

.available-scripts { 
  margin-top: 1rem; 
  border-top: 1px solid #ddd; 
  padding-top: 1rem; 
}

.available-title { 
  font-weight: 600; 
  margin-bottom: 0.75rem;
  color: #555;
}

.script-choose { 
  display: inline-block; 
  margin-right: 1rem; 
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.form-actions { 
  display: flex; 
  gap: 1rem; 
  margin-top: 2rem; 
}

.btn { 
  padding: 0.75rem 1.5rem; 
  border: none; 
  border-radius: 6px; 
  cursor: pointer; 
  font-size: 1rem; 
  transition: all 0.3s;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
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

.btn-secondary { 
  background: #6c757d; 
  color: white; 
}

.btn-secondary:hover:not(:disabled) {
  background: #5a6268;
}

.btn-danger { 
  background: #e53e3e; 
  color: white; 
}

.btn-danger:hover { 
  background: #c53030; 
}

.btn-info { 
  background: #3182ce; 
  color: white; 
}

.btn-info:hover {
  background: #2c5aa0;
}

.btn-small { 
  padding: 0.25rem 0.75rem; 
  font-size: 0.8rem; 
}

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid #f0f0f0;
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.close-icon {
  position: absolute;
  top: 12px;
  right: 12px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  color: #475569;
}
.close-icon:hover {
  background: rgba(0,0,0,0.04);
}

.header { position: relative; }
</style>
