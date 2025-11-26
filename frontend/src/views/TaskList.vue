<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
    <!-- 页头 -->
    <div class="mb-8 flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-slate-900">编排任务</h1>
        <p class="mt-1 text-sm text-slate-600">管理和执行任务编排</p>
      </div>
      <button
        @click="showNewTaskModal = true"
        class="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white shadow-md transition hover:bg-blue-700 hover:shadow-lg"
      >
        <Plus :size="20" />
        新建任务
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex flex-col items-center justify-center rounded-lg bg-white p-12 shadow-sm">
      <div class="mb-4 h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600"></div>
      <p class="text-slate-600">加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="tasks.length === 0" class="flex flex-col items-center justify-center rounded-lg bg-white p-12 shadow-sm">
      <FileText class="mb-4 text-slate-400" :size="48" />
      <h3 class="text-lg font-semibold text-slate-900">暂无任务</h3>
      <p class="mt-1 text-slate-600">还没有创建任何编排任务</p>
      <button
        @click="showNewTaskModal = true"
        class="mt-6 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white shadow-md transition hover:bg-blue-700 hover:shadow-lg"
      >
        <Plus :size="18" />
        创建第一个任务
      </button>
    </div>

    <!-- 任务列表 -->
    <div v-else class="overflow-hidden rounded-lg bg-white shadow-sm list-container">
      <div class="responsive-table">
      <table class="w-full">
        <thead>
          <tr class="border-b border-slate-200 bg-slate-50">
            <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-700">任务名称</th>
            <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-700">描述</th>
            <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-700">脚本数</th>
            <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-700">ID</th>
            <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-700">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200">
          <tr v-for="task in tasks" :key="task.id" class="transition hover:bg-blue-50">
            <td class="px-6 py-4" data-label="任务名称">
              <span class="font-semibold text-slate-900">{{ task.name }}</span>
            </td>
            <td class="px-6 py-4 text-sm text-slate-600" data-label="描述">{{ task.description || '-' }}</td>
            <td class="px-6 py-4" data-label="脚本数">
              <span class="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800">
                {{ task.scripts.length }}
              </span>
            </td>
            <td class="px-6 py-4" data-label="ID">
              <code class="rounded bg-slate-100 px-2.5 py-1 font-mono text-sm text-slate-700">{{ task.id }}</code>
            </td>
            <td class="px-6 py-4" data-label="操作">
              <div class="flex items-center gap-2 action-buttons">
                <button
                  @click="openExecute(task.id)"
                  class="inline-flex items-center justify-center rounded-lg bg-blue-100 p-2 text-blue-700 transition hover:bg-blue-200"
                  title="执行任务"
                >
                  <Play :size="18" />
                </button>
                <button
                  @click="openEditor(task)"
                  class="inline-flex items-center justify-center rounded-lg bg-green-100 p-2 text-green-700 transition hover:bg-green-200"
                  title="编辑任务"
                >
                  编辑
                </button>
                <router-link
                  :to="`/dbtasks/${task.id}/runs`"
                  class="inline-flex items-center justify-center rounded-lg bg-amber-100 p-2 text-amber-700 transition hover:bg-amber-200"
                  title="查看历史"
                >
                  <BarChart3 :size="18" />
                </router-link>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>
    <!-- 新建任务对话框 -->
    <div v-if="showNewTaskModal" class="modal-backdrop" @click.self="showNewTaskModal = false">
      <div class="modal-panel">
        <DbTaskEditor :inline="true" @close="showNewTaskModal = false" @created="onTaskCreated" />
      </div>
    </div>
    <!-- 执行任务对话框 -->
    <div v-if="showExecuteModal" class="modal-backdrop" @click.self="showExecuteModal = false">
      <div class="modal-panel">
        <DbTaskExecute :inline="true" :taskId="executeTaskId" @close="showExecuteModal = false" @executed="onExecuted" />
      </div>
    </div>
    <!-- 编辑任务对话框 -->
    <div v-if="showEditModal" class="modal-backdrop" @click.self="showEditModal = false">
      <div class="modal-panel">
        <DbTaskEditor :inline="true" :task="editTask" @close="showEditModal = false" @updated="onTaskUpdated" />
      </div>
    </div>
  </div>
</template>

<script>
import { Plus, Play, BarChart3, FileText } from 'lucide-vue-next'
import DbTaskEditor from './DbTaskEditor.vue'
import DbTaskExecute from './DbTaskExecute.vue'

export default {
  name: 'TaskList',
  components: {
    Plus,
    Play,
    BarChart3,
    FileText,
    DbTaskEditor,
    DbTaskExecute
  },
  data() {
    return {
      tasks: [],
      loading: true,
      showNewTaskModal: false,
      showExecuteModal: false,
      executeTaskId: null
      ,showEditModal: false,
      editTask: null
    }
  },
  methods: {
    openExecute(taskId) {
      this.executeTaskId = taskId
      this.showExecuteModal = true
    },
    openEditor(task) {
      this.editTask = task
      this.showEditModal = true
    },
    async loadTasks() {
      try {
        this.loading = true
        const res = await this.$http.get('/tasks/db')
        this.tasks = res.data.data || []
      } catch (error) {
        console.error('加载任务列表失败:', error)
        this.$notify?.('加载任务列表失败: ' + error.message, 'error')
      } finally {
        this.loading = false
      }
    },
    onTaskCreated(taskId) {
      // 任务创建后刷新列表并关闭对话框
      this.showNewTaskModal = false
      this.loadTasks()
      this.$notify?.('任务创建成功: ' + taskId, 'success')
    }
    ,onTaskUpdated(taskId) {
      this.showEditModal = false
      this.loadTasks()
      this.$notify?.('任务更新成功: ' + taskId, 'success')
    }
    ,onExecuted(runId) {
      this.$notify?.('任务已提交: ' + runId, 'success')
    }
  },
  mounted() {
    this.loadTasks()
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 60;
}
.modal-panel {
  width: 96%;
  max-width: 900px;
}
</style>

<style scoped>
/* Using Tailwind CSS - no custom styles needed */
</style>

<style scoped>
/* Responsive table -> card layout on small screens */
.responsive-table{width:100%;overflow-x:auto}

@media (max-width: 768px){
  .list-container { background: transparent; box-shadow: none; border: none; overflow: visible; }

  .responsive-table table,
  .responsive-table thead,
  .responsive-table tbody,
  .responsive-table th,
  .responsive-table td,
  .responsive-table tr { display:block; }

  .responsive-table thead { display:none; }

  .responsive-table tbody tr {
    margin: 0 0 16px;
    padding: 14px;
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(15,23,42,0.04);
  }

  .responsive-table tbody tr:last-child { margin-bottom: 0 }

  .responsive-table td {
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding: 10px 0;
    border-bottom: 1px solid rgba(15,23,42,0.03);
  }

  .responsive-table td::before {
    content: attr(data-label);
    font-weight: 600;
    color: #475569;
    margin-right: 12px;
  }

  .responsive-table td:last-child { border-bottom:0 }

  .action-buttons{display:flex;gap:8px}

  .modal-panel{ width: 96%; max-width: 95%; margin: 0 8px }
}
</style>
