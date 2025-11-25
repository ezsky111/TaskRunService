<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
    <div class="space-y-6">
      <!-- 任务选择器卡片 -->
      <div class="overflow-hidden rounded-lg bg-white shadow-sm">
        <div class="border-b border-slate-200 bg-gradient-to-r from-blue-50 to-slate-50 px-6 py-4">
          <h3 class="text-lg font-semibold text-slate-900">选择任务查看执行记录</h3>
          <p class="mt-1 text-sm text-slate-600">选择一个任务后，即可查看该任务的所有运行记录及详细日志</p>
        </div>

        <div class="space-y-4 px-6 py-6"  style="position: relative;">
          <!-- 搜索 + 下拉选择 -->
          <div class="space-y-2" >
            <label class="block text-sm font-semibold text-slate-700">任务</label>
            <Select
            
              v-model="selectedTaskId"
              :options="taskOptions"
              placeholder="-- 选择任务 --"
              @change="loadRuns"
            />
          </div>

          <!-- 任务信息（如果已选择） -->
          <div v-if="selectedTaskId && taskInfo" class="space-y-2">
            <div class="rounded-lg bg-blue-50 p-4">
              <div class="flex items-start justify-between">
                <div>
                  <p class="text-xs font-semibold text-blue-700 uppercase">当前任务</p>
                  <p class="mt-1 text-lg font-bold text-blue-900">{{ taskInfo.name }}</p>
                  <p v-if="taskInfo.description" class="mt-1 text-sm text-blue-700">
                    {{ taskInfo.description }}
                  </p>
                </div>
                <div class="text-right">
                  <p class="text-xs text-blue-600">ID: {{ taskInfo.id }}</p>
                  <p class="mt-2 text-xs font-semibold text-blue-600">
                    {{ taskInfo.scripts?.length || 0 }} 个脚本
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 运行列表（当选择任务时显示） -->
      <div v-if="selectedTaskId">
        <RunsList
          :runs="runs"
          :task-info="taskInfo"
          :loading="loading"
          :show-back-button="false"
          @refresh="loadRuns"
          @view-logs="viewLogs"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { dbTaskApi } from '../api/index.js'
import { Select } from '@/components/ui'
import RunsList from '@/components/RunsList.vue'

export default {
  name: 'TaskLogs',
  components: { RunsList, Select },
  data() {
    return {
      tasks: [],
      runs: [],
      taskInfo: null,
      selectedTaskId: '',
      loading: false
    }
  },
  computed: {
    taskOptions() {
      return this.tasks.map((task) => ({
        value: task.id,
        label: `${task.name}${task.description ? ` - ${task.description}` : ''}`
      }))
    }
  },
  methods: {
    async loadTasks() {
      try {
        this.loading = true
        const res = await dbTaskApi.listTasks()
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
        this.taskInfo = null
        return
      }
      try {
        this.loading = true
        // 从已加载的任务列表中查找任务详情
        this.taskInfo = this.tasks.find(t => t.id == this.selectedTaskId) || null
        const runsRes = await dbTaskApi.getTaskRuns(this.selectedTaskId)
        this.runs = runsRes.data.data || []
      } catch (error) {
        console.error('加载运行记录失败:', error)
      } finally {
        this.loading = false
      }
    },
    async viewLogs(runId, callback) {
      try {
        const [logsRes, contextsRes] = await Promise.all([
          dbTaskApi.getRunLogs(runId),
          dbTaskApi.getRunContexts(runId)
        ])
        const logs = logsRes.data.data || []
        const contexts = contextsRes.data.data || []
        callback(logs, contexts)
      } catch (error) {
        console.error('加载日志失败:', error)
        callback([], [])
      }
    }
  },
  mounted() {
    this.loadTasks()
  }
}
</script>

<style>
.btn-primary { background: #667eea; color: white; }
.btn-small { padding: 0.25rem 0.75rem; font-size: 0.8rem; }
</style>
