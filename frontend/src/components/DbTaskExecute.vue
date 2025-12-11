<template>
  <el-dialog v-model:model-value="visible" title="执行任务" width="560px" :destroy-on-close="true">
    <el-form :model="{}" label-width="140px">
        <span>环境变量（JSON格式）</span>
        <el-input
          type="textarea"
          v-model="contextStr"
          style="margin-top:10px"
          :rows="8"
          placeholder='{"key": "value"}'
        />

      <div v-if="runId" class="result">
        <el-alert title="任务已提交" type="success" :description="'运行ID: ' + runId" show-icon />
      </div>
    </el-form>

    <template #footer>
      <div style="text-align:right">
        <el-button @click="closeDialog" :disabled="loading">取消</el-button>
        <el-button type="primary" :loading="loading" @click="executeTask">执行</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchExecuteDbTask } from '@/api/task-db'

export default {
  name: 'DbTaskExecute',
  props: {
    taskId: { type: [String, Number], required: true },
    modelValue: { type: Boolean, default: false }
  },
  emits: ['update:modelValue', 'executed', 'error'],
  setup(props, { emit }) {
    const contextStr = ref('')
    const runId = ref(null)
    const loading = ref(false)

    const visible = computed({
      get: () => props.modelValue,
      set: (v) => emit('update:modelValue', v)
    })

    const closeDialog = () => {
      visible.value = false
    }

    const executeTask = async () => {
      let context = {}
      if (contextStr.value.trim()) {
        try {
          context = JSON.parse(contextStr.value)
        } catch (e) {
          ElMessage.warning('环境变量格式错误，应为JSON')
          return
        }
      }

      loading.value = true
      try {
        const res = await fetchExecuteDbTask(props.taskId, context)
        const data = res.data || {}
        const rid = data.data?.run_id || data.data?.runId || data.run_id || data.runId || data.data
        runId.value = rid || null
        ElMessage.success('任务已提交' + (rid ? (': ' + rid) : ''))
        emit('executed', rid)
        visible.value = false
      } catch (err) {
        ElMessage.error('执行失败: ' + (err.response?.data?.message || err.message || ''))
        emit('error', err)
      } finally {
        loading.value = false
      }
    }

    return { contextStr, runId, loading, executeTask, closeDialog, visible }
  }
}
</script>

<style scoped>
.result { margin-top:12px }
</style>
