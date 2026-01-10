import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => config,
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data

    // 文件下载直接返回
    if (response.config.responseType === 'blob') {
      return response
    }

    // 处理业务响应
    if (res.success === false) {
      ElMessage.error(res.error || '操作失败')
      return Promise.reject(new Error(res.error || '操作失败'))
    }

    return res
  },
  error => {
    console.error('响应错误:', error)

    if (error.response) {
      const status = error.response.status
      const messages = {
        404: '请求的资源不存在',
        500: '服务器错误,请稍后重试'
      }
      ElMessage.error(messages[status] || error.response.data?.error || '网络请求失败')
    } else if (error.request) {
      ElMessage.error('网络连接失败,请检查网络')
    } else {
      ElMessage.error('请求配置错误')
    }

    return Promise.reject(error)
  }
)

// 创建 API 辅助函数
export function createApi(url, method = 'get') {
  return (data, config) => {
    const params = method === 'get' ? { params: data } : { data }
    return request({ url, method, ...params, ...config })
  }
}

export default request
