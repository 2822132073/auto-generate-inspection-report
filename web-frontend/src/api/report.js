import request from './request'

// 获取模板列表
export function getTemplates() {
  return request({
    url: '/templates',
    method: 'get'
  })
}

// 生成报告
export function generateReport(projectId, data) {
  return request({
    url: `/projects/${projectId}/report`,
    method: 'post',
    data
  })
}

// 下载报告
export function downloadReport(projectId) {
  return request({
    url: `/projects/${projectId}/report`,
    method: 'get',
    responseType: 'blob'
  })
}
