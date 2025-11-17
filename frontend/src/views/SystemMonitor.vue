<template>
  <div class="system-monitor">
    <h2>系统监控</h2>
    
    <div class="monitor-grid">
      <div class="monitor-card">
        <h3>系统信息</h3>
        <div v-if="systemInfo" class="info-grid">
          <div class="info-item">
            <span class="label">CPU 使用率:</span>
            <span class="value">{{ systemInfo.cpu_percent }}%</span>
          </div>
          <div class="info-item">
            <span class="label">内存使用:</span>
            <span class="value">{{ (systemInfo.memory.percent).toFixed(2) }}%</span>
          </div>
          <div class="info-item">
            <span class="label">可用内存:</span>
            <span class="value">{{ formatBytes(systemInfo.memory.available) }}</span>
          </div>
          <div class="info-item">
            <span class="label">磁盘使用:</span>
            <span class="value">{{ (systemInfo.disk.percent).toFixed(2) }}%</span>
          </div>
        </div>
      </div>
      
      <div class="monitor-card">
        <h3>当前进程</h3>
        <div v-if="processInfo" class="info-grid">
          <div class="info-item">
            <span class="label">PID:</span>
            <span class="value">{{ processInfo.pid }}</span>
          </div>
          <div class="info-item">
            <span class="label">进程名:</span>
            <span class="value">{{ processInfo.name }}</span>
          </div>
          <div class="info-item">
            <span class="label">内存占用:</span>
            <span class="value">{{ formatBytes(processInfo.memory_info.rss) }}</span>
          </div>
          <div class="info-item">
            <span class="label">CPU 占用:</span>
            <span class="value">{{ processInfo.cpu_percent }}%</span>
          </div>
          <div class="info-item">
            <span class="label">线程数:</span>
            <span class="value">{{ processInfo.num_threads }}</span>
          </div>
          <div class="info-item">
            <span class="label">状态:</span>
            <span class="value">{{ processInfo.status }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="monitor-card">
      <h3>Python 进程列表</h3>
      <table v-if="processes.length > 0" class="process-table">
        <thead>
          <tr>
            <th>PID</th>
            <th>进程名</th>
            <th>状态</th>
            <th>内存 (MB)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="proc in processes" :key="proc.pid">
            <td>{{ proc.pid }}</td>
            <td>{{ proc.name }}</td>
            <td>{{ proc.status }}</td>
            <td>{{ (proc.memory_rss / 1024 / 1024).toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else>暂无 Python 进程</p>
    </div>
    
    <button @click="refreshMonitor" class="btn btn-primary" style="margin-top: 2rem;">刷新</button>
  </div>
</template>

<script>
import { systemApi } from '../api/index.js'

export default {
  name: 'SystemMonitor',
  data() {
    return {
      systemInfo: null,
      processInfo: null,
      processes: [],
      refreshInterval: null
    }
  },
  methods: {
    async loadMonitorData() {
      try {
        const [sysRes, procRes, allProcsRes] = await Promise.all([
          systemApi.getSystemInfo(),
          systemApi.getProcessInfo(),
          systemApi.getAllProcesses()
        ])
        
        this.systemInfo = sysRes.data.data
        this.processInfo = procRes.data.data
        this.processes = allProcsRes.data.data
      } catch (error) {
        console.error('加载监控数据失败:', error)
      }
    },
    refreshMonitor() {
      this.loadMonitorData()
    },
    formatBytes(bytes) {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
    }
  },
  mounted() {
    this.loadMonitorData()
    this.refreshInterval = setInterval(() => this.loadMonitorData(), 10000)
  },
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
    }
  }
}
</script>

<style scoped>
.system-monitor {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.system-monitor h2 {
  font-size: 1.5rem;
  margin-bottom: 2rem;
}

.monitor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.monitor-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1.5rem;
  background: #f9f9f9;
}

.monitor-card h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  padding: 0.75rem;
  background: white;
  border-radius: 4px;
}

.label {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.25rem;
}

.value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #667eea;
}

.process-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.process-table th {
  background: #f5f5f5;
  padding: 0.75rem;
  text-align: left;
  border-bottom: 2px solid #ddd;
}

.process-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #ddd;
}

.process-table tr:hover {
  background: #f9f9f9;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
}
</style>
