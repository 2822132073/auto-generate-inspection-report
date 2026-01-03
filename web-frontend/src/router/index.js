import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'ProjectList',
    component: () => import('@/views/ProjectList.vue'),
    meta: { title: '项目列表' }
  },
  {
    path: '/projects/:projectCode',
    name: 'ProjectDetail',
    component: () => import('@/views/ProjectDetail.vue'),
    meta: { title: '项目详情' }
  },
  {
    path: '/projects/:projectCode/hosts/:hostname',
    name: 'HostInspections',
    component: () => import('@/views/HostInspections.vue'),
    meta: { title: '主机巡检记录' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 服务器巡检报告系统` : '服务器巡检报告系统'
  next()
})

// 全局后置守卫
router.afterEach(() => {
  // 滚动到页面顶部
  window.scrollTo(0, 0)
})

export default router
