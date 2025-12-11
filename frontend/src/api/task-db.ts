// 任务编排相关接口（基于项目的 request 封装，保持与旧调用返回结构兼容）
import request from '@/utils/http'

export function fetchDbListTasks(params?: Record<string, any>) {
  return request.get({ url: '/api/tasks/db', params })
}

export function fetchListScript() {
  return request.get({ url: '/api/tasks' })
}

export function fetchCreateDbTask(data: any) {
  return request.post({ url: '/api/tasks/db', data })
}

export function fetchUpdateDbTask(taskId: string | number, data: any) {
  return request.put({ url: `/api/tasks/db/${taskId}`, data })
}

export function fetchExecuteDbTask(taskId: string | number, context: any) {
  return request.post({ url: `/api/tasks/db/${taskId}/execute`, data: { context } })
}

export function fetchGetDbTaskRuns(taskId: string | number) {
  return request.get({ url: `/api/tasks/db/${taskId}/runs` })
}
export function fetchGetAllDbTaskRuns() {
  return request.get({ url: `/api/tasks/db/runs` })
}
export function fetchGetDbRunLogs(runId: string | number) {
  return request.get({ url: `/api/tasks/db/runs/${runId}/logs` })
}

export function fetchGetDbRunContexts(runId: string | number) {
  return request.get({ url: `/api/tasks/db/runs/${runId}/contexts` })
}

// 普通任务接口
export function fetchListTasks() {
  return request.get({ url: '/api/tasks' })
}

export function fetchGetTask(taskId: string | number) {
  return request.get({ url: `/api/tasks/${taskId}` })
}

export function fetchCreateTask(data: any) {
  return request.post({ url: '/api/tasks', data })
}

export function fetchUpdateTask(taskId: string | number, data: any) {
  return request.put({ url: `/api/tasks/${taskId}`, data })
}

export function fetchDeleteTask(taskId: string | number) {
  return request.del({ url: `/api/tasks/${taskId}` })
}

export function fetchExecuteTask(taskId: string | number, params: any) {
  return request.post({ url: `/api/tasks/${taskId}/execute`, data: { params } })
}

export function fetchGetTaskStatus(runId: string | number) {
  return request.get({ url: `/api/tasks/runs/${runId}` })
}

export function fetchGetActiveTasks() {
  return request.get({ url: '/api/tasks/runs' })
}
