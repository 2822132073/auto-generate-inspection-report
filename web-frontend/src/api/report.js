import request, { createApi } from './request'

// 获取模板列表
export const getTemplates = createApi('/templates')

// 生成报告
export const generateReport = (id, data) => createApi(`/projects/${id}/report`, 'post')(data)

// 下载报告（需要特殊配置 responseType）
export function downloadReport(projectId) {
  return request({
    url: `/projects/${projectId}/report`,
    method: 'get',
    responseType: 'blob'
  })
}
