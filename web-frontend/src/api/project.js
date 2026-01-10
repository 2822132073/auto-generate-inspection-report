import { createApi } from './request'

// 获取系统统计信息
export const getStats = createApi('/stats')

// 获取项目列表
export const getProjects = createApi('/projects')

// 根据项目代码获取项目
export const getProjectByCode = (code) => createApi(`/projects/by-code/${code}`)()

// 获取项目统计信息
export const getProjectStatistics = (id) => createApi(`/projects/${id}/statistics`)()

// 获取项目下的主机列表
export const getProjectHosts = (id) => createApi(`/projects/${id}/hosts`)()

// 创建项目
export const createProject = createApi('/projects', 'post')
