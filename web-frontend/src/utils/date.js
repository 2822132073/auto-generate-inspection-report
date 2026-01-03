import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

// 格式化日期时间
export function formatDateTime(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return '-'
  return dayjs(date).format(format)
}

// 格式化为相对时间
export function formatRelativeTime(date) {
  if (!date) return '-'
  return dayjs(date).fromNow()
}

// 格式化日期
export function formatDate(date) {
  return formatDateTime(date, 'YYYY-MM-DD')
}
