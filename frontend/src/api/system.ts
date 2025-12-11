// 系统监控相关接口（基于项目的 request 封装）
import request from '@/utils/http'

export function fetchSystemInfo() {
  return request.get({ url: '/api/system/info' })
}

export function fetchSystemProcess() {
  return request.get({ url: '/api/system/process' })
}

export function fetchSystemProcesses() {
  return request.get({ url: '/api/system/processes' })
}

export default {
  fetchSystemInfo,
  fetchSystemProcess,
  fetchSystemProcesses
}
