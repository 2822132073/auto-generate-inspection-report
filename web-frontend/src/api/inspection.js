import request from './request'

// 获取巡检记录列表
export function getInspections(params) {
  return request({
    url: '/inspections',
    method: 'get',
    params
  })
}

// 获取巡检记录详情
export function getInspectionDetail(id) {
  return request({
    url: `/inspections/${id}`,
    method: 'get'
  })
}
