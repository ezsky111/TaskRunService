<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
    <RunsList
      :runs="runs"
      :task-info="taskInfo"
      :loading="loading"
      :show-back-button="true"
      @back="goBack"
      @refresh="loadRuns"
      @view-logs="viewLogs"
    />
  </div>
</template>

<script>
import { dbTaskApi } from '../api/index.js'
import RunsList from '@/components/RunsList.vue'

export default {
  name: 'DbTaskRuns',
  components: { RunsList },
  props: {
    taskId: [String, Number]
  },
  data() {
    return {
      runs: [],
      taskInfo: null,
      loading: false
    }
  },
  methods: {
    async loadRuns() {
      this.loading = true
      try {
        const res = await dbTaskApi.getTaskRuns(Number(this.taskId))
        if (res.data.success) {
          this.runs = res.data.data || []
          // 加载任务信息
          await this.loadTaskInfo()
        }
      } catch (error) {
        console.error('加载运行记录失败:', error)
      } finally {
        this.loading = false
      }
    },
    async loadTaskInfo() {
      try {
        const res = await this.$http.get(`/tasks/db/${this.taskId}`)
        if (res.data.success) {
          this.taskInfo = res.data.data
        }
      } catch (error) {
        console.error('加载任务信息失败:', error)
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
        // 调用回调传递数据
        callback(logs, contexts)
      } catch (error) {
        console.error('加载日志失败:', error)
        callback([], [])
      }
    },
    goBack() {
      this.$router.back()
    }
  },
  mounted() {
    this.loadRuns()
  }
}
</script>

<style scoped>
/* Using Tailwind CSS - no custom styles needed */
</style>
