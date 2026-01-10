import { createApi } from './request'

// 获取巡检记录列表
export const getInspections = createApi('/inspections')

// 获取巡检记录详情
export const getInspectionDetail = (id) => createApi(`/inspections/${id}`)()

// 获取截图生成状态
export const getScreenshotStatus = (id) => createApi(`/inspections/${id}/screenshot-status`)()

// 重新生成截图
export const regenerateScreenshots = (id) => createApi(`/inspections/${id}/regenerate-screenshots`, 'post')()
