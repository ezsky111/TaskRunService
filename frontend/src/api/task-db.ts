// 任务编排相关接口（仿照 frontend/src/api/index.js 的 dbTaskApi）
import axios from 'axios'

const api = axios.create({
  baseURL: '/backend-api',
  timeout: 30000
})

export const dbTaskApi = {
  listTasks: () => api.get('/tasks/db'),
  listScript: () => api.get('/tasks'),
  createTask: (data: any) => api.post('/tasks/db', data),
  updateTask: (taskId: string|number, data: any) => api.put(`/tasks/db/${taskId}`, data),
  executeTask: (taskId: string|number, context: any) => api.post(`/tasks/db/${taskId}/execute`, { context }),
  getTaskRuns: (taskId: string|number) => api.get(`/tasks/db/${taskId}/runs`),
  getRunLogs: (runId: string|number) => api.get(`/tasks/db/runs/${runId}/logs`),
  getRunContexts: (runId: string|number) => api.get(`/tasks/db/runs/${runId}/contexts`)
}

export const taskApi = {
  listTasks: () => api.get('/tasks'),
  getTask: (taskId: string|number) => api.get(`/tasks/${taskId}`),
  createTask: (data: any) => api.post('/tasks', data),
  updateTask: (taskId: string|number, data: any) => api.put(`/tasks/${taskId}`, data),
  deleteTask: (taskId: string|number) => api.delete(`/tasks/${taskId}`),
  executeTask: (taskId: string|number, params: any) => api.post(`/tasks/${taskId}/execute`, { params }),
  getTaskStatus: (runId: string|number) => api.get(`/tasks/runs/${runId}`),
  getActiveTasks: () => api.get('/tasks/runs')
}
