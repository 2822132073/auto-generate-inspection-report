import request from './request'

// 获取系统统计信息
export function getStats() {
  return request({
    url: '/stats',
    method: 'get'
  })
}

// 获取项目列表
export function getProjects(params) {
  return request({
    url: '/projects',
    method: 'get',
    params
  })
}

// 根据项目代码获取项目
export function getProjectByCode(projectCode) {
  return request({
    url: `/projects/by-code/${projectCode}`,
    method: 'get'
  })
}

// 获取项目统计信息
export function getProjectStatistics(projectId) {
  return request({
    url: `/projects/${projectId}/statistics`,
    method: 'get'
  })
}

// 获取项目下的主机列表
export function getProjectHosts(projectId) {
  return request({
    url: `/projects/${projectId}/hosts`,
    method: 'get'
  })
}

// 创建项目
export function createProject(data) {
  return request({
    url: '/projects',
    method: 'post',
    data
  })
}
