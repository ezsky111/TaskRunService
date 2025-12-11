<!-- 工作台页面 -->
<template>
  <div>
    <!-- <CardList></CardList> -->

    <!-- 系统监控板块 -->
    <ElCard class="mb-4">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <h3>系统监控</h3>
        <ElButton type="primary" size="small" @click="refreshMonitor">刷新</ElButton>
      </div>

      <ElRow :gutter="20" style="margin-top:12px;">
        <ElCol :xs="24" :sm="12" :md="6">
          <div class="monitor-item">
            <div class="label">CPU 使用率</div>
            <div class="value">{{ formatPercent(systemInfo?.cpu_percent) }}%</div>
          </div>
        </ElCol>
        <ElCol :xs="24" :sm="12" :md="6">
          <div class="monitor-item">
            <div class="label">内存使用</div>
            <div class="value">{{ formatPercent(systemInfo?.memory?.percent) }}%</div>
            <div class="sub">可用: {{ formatBytes(systemInfo?.memory?.available) }}</div>
          </div>
        </ElCol>
        <ElCol :xs="24" :sm="12" :md="6">
          <div class="monitor-item">
            <div class="label">磁盘使用</div>
            <div class="value">{{ formatPercent(systemInfo?.disk?.percent) }}%</div>
          </div>
        </ElCol>
        <ElCol :xs="24" :sm="12" :md="6">
          <div class="monitor-item">
            <div class="label">当前进程</div>
            <div class="value">PID: {{ processInfo?.pid ?? '—' }}</div>
            <div class="sub">{{ processInfo?.name ?? '—' }} · CPU {{ formatPercent(processInfo?.cpu_percent) }}%</div>
          </div>
        </ElCol>
      </ElRow>

      <div style="margin-top:12px">
        <ElTable :data="processes" v-if="processes.length > 0" style="width:100%">
          <ElTableColumn prop="pid" label="PID" width="100" />
          <ElTableColumn prop="name" label="进程名" />
          <ElTableColumn prop="status" label="状态" width="120" />
          <ElTableColumn label="内存(MB)">
            <template #default="{ row }">{{ (row.memory_rss / 1024 / 1024).toFixed(2) }}</template>
          </ElTableColumn>
        </ElTable>
        <div v-else style="color:var(--el-text-color-secondary)">暂无 Python 进程</div>
      </div>
    </ElCard>

    <!-- <ElRow :gutter="20">
      <ElCol :sm="24" :md="12" :lg="10">
        <ActiveUser />
      </ElCol>
      <ElCol :sm="24" :md="12" :lg="14">
        <SalesOverview />
      </ElCol>
    </ElRow>

    <ElRow :gutter="20">
      <ElCol :sm="24" :md="24" :lg="12">
        <NewUser />
      </ElCol>
      <ElCol :sm="24" :md="12" :lg="6">
        <Dynamic />
      </ElCol>
      <ElCol :sm="24" :md="12" :lg="6">
        <TodoList />
      </ElCol>
    </ElRow>

    <AboutProject /> -->
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { fetchSystemInfo, fetchSystemProcess, fetchSystemProcesses } from '@/api/system'

import CardList from './modules/card-list.vue'
import ActiveUser from './modules/active-user.vue'
import SalesOverview from './modules/sales-overview.vue'
import NewUser from './modules/new-user.vue'
import Dynamic from './modules/dynamic-stats.vue'
import TodoList from './modules/todo-list.vue'
import AboutProject from './modules/about-project.vue'

defineOptions({ name: 'Console' })

const systemInfo = ref<any | null>(null)
const processInfo = ref<any | null>(null)
const processes = ref<any[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

let refreshInterval: number | null = null

async function loadMonitorData() {
  loading.value = true
  error.value = null
  try {
    const [sysRes, procRes, allRes] = (await Promise.all([
      fetchSystemInfo(),
      fetchSystemProcess(),
      fetchSystemProcesses()
    ])) as any[]

    systemInfo.value = sysRes ?? null
    processInfo.value = procRes ?? null
    processes.value = Array.isArray(allRes) ? allRes : []
  } catch (e: any) {
    console.error('loadMonitorData error:', e)
    error.value = e?.message || '加载监控数据失败'
  } finally {
    loading.value = false
  }
}

function refreshMonitor() {
  loadMonitorData()
}

function formatBytes(bytes: number | undefined) {
  if (!bytes && bytes !== 0) return '—'
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(Number(bytes)) / Math.log(k))
  return (Number(bytes) / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

function formatPercent(value: number | undefined | null) {
  if (value === null || typeof value === 'undefined') return '—'
  return Number(value).toFixed(2)
}

onMounted(() => {
  loadMonitorData()
  refreshInterval = window.setInterval(() => loadMonitorData(), 10000)
})

onUnmounted(() => {
  if (refreshInterval) window.clearInterval(refreshInterval)
})
</script>

<style scoped>
.monitor-item { padding: 12px; background: var(--el-card-bg-color); border-radius: 6px; }
.monitor-item .label { color: var(--el-text-color-secondary); font-size: 12px }
.monitor-item .value { font-size: 18px; font-weight: 600; margin-top: 6px }
.monitor-item .sub { font-size: 12px; color: var(--el-text-color-secondary); margin-top:6px }
</style>
