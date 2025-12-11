<template>
  <div class="task-page art-full-height">
    <div style="margin-bottom:12px">
      <TaskSearch v-model="searchForm" @search="handleSearch" @reset="resetSearchParams" />
    </div>

    <ElCard class="art-table-card" shadow="never">
      <ArtTableHeader v-model:columns="columnChecks" :loading="loading" @refresh="refreshData">
        <template #left>
          <ElSpace>
            <ElButton @click="createTask" v-ripple>新建任务</ElButton>
          </ElSpace>
        </template>
      </ArtTableHeader>

      <ArtTable
          :loading="loading"
            :data="tableData"
        :columns="columns"
        :pagination="pagination"
        @selection-change="handleSelectionChange"
        @pagination:size-change="handleSizeChange"
        @pagination:current-change="handleCurrentChange"
      />
    </ElCard>
    <TaskDialog v-model="dialogVisible" :type="dialogType" :task="currentTask || undefined" @submit="onDialogSubmit" />
    <DbTaskExecute v-model="showExecuteDialog" :task-id="selectedTaskId" @executed="onExecuted" @error="onExecuteError" />
  </div>
</template>

<script setup lang="ts">
import { h, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTable } from '@/hooks/core/useTable'
import ArtButtonTable from '@/components/core/forms/art-button-table/index.vue'
import { ElTag, ElMessage, ElMessageBox, ElButton, ElSpace, ElCard } from 'element-plus'
import TaskDialog from './modules/task-dialog.vue'
import TaskSearch from './modules/task-search.vue'
import DbTaskExecute from '@/components/DbTaskExecute.vue'

const router = useRouter()
type TaskItem = {
  id: string | number
  name: string
  description?: string
}

// API 函数：useTable 需要接收一个返回 Promise 的函数
const apiFn = async (params: Record<string, any>) => {
  const queryObj: Record<string, string> = {}
  Object.entries(params || {}).forEach(([k, v]) => {
    if (v !== undefined && v !== null) queryObj[k] = String(v)
  })
  const query = new URLSearchParams(queryObj).toString()
  const res = await fetch(`/backend-api/tasks/db?${query}`)
  return res.json()
}

const {
  columns,
  columnChecks,
  data,
  loading,
  pagination,
  getData,
  searchParams,
  resetSearchParams,
  handleSizeChange,
  handleCurrentChange,
  refreshData
} = useTable({
  core: {
    apiFn,
    apiParams: { current: 1, size: 10 },
    columnsFactory: () => [
      { type: 'selection' },
      { prop: 'id', label: 'ID', width: 90 },
      {
        prop: 'name',
        label: '任务名',
        formatter: (row: any) => (row as TaskItem).name
      },
      {
        prop: 'description',
        label: '任务描述',
        formatter: (row: any) => (row as TaskItem).description || '-'
      },
      {
        prop: 'operation',
        label: '操作',
        width: 260,
        fixed: 'right',
        formatter: (row: any) =>
          h('div', [
            h(ArtButtonTable, {
              type: 'edit',
              onClick: () => edit(row as TaskItem)
            }),
            h(ArtButtonTable, {
              type: 'delete',
              onClick: () => deleteTask(row as TaskItem)
            }),
            h(ArtButtonTable, {
              type: 'run',
              onClick: () => run(row as TaskItem)
            }),
            h(ArtButtonTable, {
              type: 'view',
              onClick: () => viewRuns(row as TaskItem)
            })
          ])
      }
    ]
  }
})

const tableData = computed(() => data.value as Record<string, any>[])

const searchForm = ref({ keyword: '' })

const handleSearch = () => {
  Object.assign(searchParams, { keyword: searchForm.value.keyword, current: 1 })
  getData()
}

const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit' | 'view'>('add')
const currentTask = ref<TaskItem | null>(null)

const showExecuteDialog = ref(false)
const selectedTaskForRun = ref(null as null | TaskItem | string | number)

const selectedTaskId = computed(() => {
  const v = selectedTaskForRun.value
  if (v === null) return undefined
  if (typeof v === 'object') return (v as TaskItem).id
  return v
})

const createTask = () => {
  dialogType.value = 'add'
  currentTask.value = null
  dialogVisible.value = true
}

const onDialogSubmit = async () => {
  // 刷新列表
  await refreshData()
}

const view = (row: TaskItem) => {
  dialogType.value = 'view'
  currentTask.value = row
  dialogVisible.value = true
}

const edit = (row: TaskItem) => {
  dialogType.value = 'edit'
  currentTask.value = row
  dialogVisible.value = true
}

const run = async (row: TaskItem) => {
  selectedTaskForRun.value = row
  showExecuteDialog.value = true
}

const viewRuns = (row: TaskItem) => {
  router.push({ path: '/task/run', query: { taskId: row.id } })
}

const onExecuted = async (runId: string | number | null) => {
  // 组件已发起执行并通过 ElMessage 报告成功；此处关闭对话并刷新列表
  showExecuteDialog.value = false
  await refreshData()
}

const onExecuteError = (err: any) => {
  console.error('execute error', err)
  ElMessage.error('执行失败')
}

const deleteTask = async (row: TaskItem) => {
  try {
    await ElMessageBox.confirm('确认删除该任务？', '删除确认', { type: 'warning' })
    const res = await fetch(`/backend-api/tasks/${row.id}`, { method: 'DELETE' })
    const dataRes = await res.json()
    if (res.ok && dataRes.success) {
      ElMessage.success(dataRes.message || '删除成功')
      // useTable 提供 refreshRemove 等方法，但 refreshData 可保证刷新
      await refreshData()
    } else {
      ElMessage.error(dataRes.message || '删除失败')
    }
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

const handleSelectionChange = (selection: any[]) => {
  console.log('selection', selection)
}

const statusType = (status?: string) => {
  if (!status) return 'info'
  const s = String(status).toLowerCase()
  if (['success', 'completed', 'done'].includes(s)) return 'success'
  if (['failed', 'error'].includes(s)) return 'danger'
  if (['running', 'in-progress'].includes(s)) return 'warning'
  return 'info'
}
</script>

<style scoped>
.task-list { padding: 16px }
</style>
