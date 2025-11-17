// 数据库任务编排相关接口
export const dbTaskApi = {
  createTask: (data) => api.post('/tasks/db', data),
  executeTask: (taskId, context) => api.post(`/tasks/db/${taskId}/execute`, { context }),
  getTaskRuns: (taskId) => api.get(`/tasks/db/${taskId}/runs`),
  getRunLogs: (runId) => api.get(`/tasks/db/runs/${runId}/logs`),
  getRunContexts: (runId) => api.get(`/tasks/db/runs/${runId}/contexts`)
}
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

export const taskApi = {
  listTasks: () => api.get('/tasks'),
  getTask: (taskId) => api.get(`/tasks/${taskId}`),
  createTask: (data) => api.post('/tasks', data),
  updateTask: (taskId, data) => api.put(`/tasks/${taskId}`, data),
  deleteTask: (taskId) => api.delete(`/tasks/${taskId}`),
  executeTask: (taskId, params) => api.post(`/tasks/${taskId}/execute`, { params }),
  getTaskStatus: (runId) => api.get(`/tasks/runs/${runId}`),
  getActiveTasks: () => api.get('/tasks/runs')
}

export const logApi = {
  listLogs: () => api.get('/logs'),
  getLog: (taskId, runId) => api.get(`/logs/${taskId}_${runId}.log`),
  downloadLog: (taskId, runId) => api.get(`/logs/${taskId}_${runId}.log/download`, { responseType: 'blob' }),
  getAppLog: (lines = 100) => api.get('/logs/app.log', { params: { lines } })
}

export const systemApi = {
  getSystemInfo: () => api.get('/system/info'),
  getProcessInfo: () => api.get('/system/process'),
  getAllProcesses: () => api.get('/system/processes'),
  healthCheck: () => api.get('/system/health')
}

export default api
