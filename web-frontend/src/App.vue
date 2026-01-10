<template>
  <el-config-provider :locale="zhCn">
    <div id="app" :class="{ 'dark-mode': isDarkMode }">
      <!-- 动态背景层 -->
      <div class="background-layer">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
        <div class="gradient-orb orb-3"></div>
        <div class="grid-pattern"></div>
      </div>

      <!-- 磨砂玻璃导航栏 -->
      <header class="glass-header">
        <div class="header-content">
          <div class="logo" @click="$router.push('/')">
            <div class="logo-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 17L10 11L15 16L20 11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M4 7H20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M12 7V11" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <span class="title">服务器巡检系统</span>
          </div>

          <nav class="nav-center">
            <router-link to="/" class="nav-item" :class="{ active: route.path === '/' }">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="7" height="7"/>
                <rect x="14" y="3" width="7" height="7"/>
                <rect x="14" y="14" width="7" height="7"/>
                <rect x="3" y="14" width="7" height="7"/>
              </svg>
              <span>项目列表</span>
            </router-link>
            <div class="breadcrumb">
              <span v-for="(item, index) in breadcrumbs" :key="index" class="crumb">
                <template v-if="index > 0">
                  <svg class="crumb-separator" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="9 18 15 12 9 6"/>
                  </svg>
                </template>
                <router-link v-if="item.path" :to="item.path">{{ item.title }}</router-link>
                <span v-else>{{ item.title }}</span>
              </span>
            </div>
          </nav>

          <div class="header-right">
            <div class="stats-glass" v-if="stats">
              <div class="stat-item">
                <span class="stat-label">项目</span>
                <span class="stat-value">{{ stats.total_projects }}</span>
              </div>
              <div class="stat-divider"></div>
              <div class="stat-item">
                <span class="stat-label">主机</span>
                <span class="stat-value stat-highlight">{{ stats.total_hosts }}</span>
              </div>
            </div>

            <button class="theme-toggle" @click="toggleTheme" :title="isDarkMode ? '切换浅色' : '切换深色'">
              <svg v-if="!isDarkMode" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="5"/>
                <line x1="12" y1="1" x2="12" y2="3"/>
                <line x1="12" y1="21" x2="12" y2="23"/>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                <line x1="1" y1="12" x2="3" y2="12"/>
                <line x1="21" y1="12" x2="23" y2="12"/>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
              </svg>
            </button>
          </div>
        </div>
      </header>

      <!-- 主内容区域 -->
      <main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>

      <!-- 底部 -->
      <footer class="glass-footer">
        <div class="footer-content">
          <span>© 2026 服务器巡检报告系统</span>
          <span class="footer-divider">|</span>
          <span>精心打造 · 高效运维</span>
        </div>
      </footer>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getStats } from '@/api/project'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

const route = useRoute()
const stats = ref(null)
const isDarkMode = ref(false)

// 从本地存储加载主题
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDarkMode.value = true
  }
})

// 切换主题
const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
}

// 面包屑导航
const breadcrumbs = computed(() => {
  const crumbs = []

  if (route.params.projectCode) {
    crumbs.push({
      title: decodeURIComponent(route.params.projectCode),
      path: `/projects/${route.params.projectCode}`
    })
  }

  if (route.params.hostname) {
    crumbs.push({
      title: decodeURIComponent(route.params.hostname),
      path: null
    })
  }

  return crumbs
})

// 获取统计信息
const fetchStats = async () => {
  try {
    const res = await getStats()
    stats.value = res.data
  } catch (error) {
    console.error('获取统计信息失败:', error)
  }
}

fetchStats()

// 路由变化时刷新统计
watch(() => route.path, () => {
  fetchStats()
})
</script>

<style>
/* ===== CSS 变量系统（全局） ===== */
:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --primary-gradient-hover: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);

  --glass-bg: rgba(255, 255, 255, 0.7);
  --glass-border: rgba(255, 255, 255, 0.3);
  --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);

  --text-primary: #1a1a2e;
  --text-secondary: #4a4a68;
  --text-muted: #9ca3af;

  --bg-primary: #f8fafc;
  --bg-secondary: #ffffff;
  --bg-elevated: #ffffff;

  --border-color: rgba(0, 0, 0, 0.08);
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.04);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.12);

  --orb-1: rgba(102, 126, 234, 0.4);
  --orb-2: rgba(118, 75, 162, 0.3);
  --orb-3: rgba(240, 147, 251, 0.3);
}

.dark-mode {
  --glass-bg: rgba(15, 23, 42, 0.8);
  --glass-border: rgba(255, 255, 255, 0.1);
  --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);

  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;

  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-elevated: #334155;

  --border-color: rgba(255, 255, 255, 0.08);
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.2);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.4);

  --orb-1: rgba(102, 126, 234, 0.2);
  --orb-2: rgba(118, 75, 162, 0.15);
  --orb-3: rgba(240, 147, 251, 0.15);
}

/* ===== 基础布局 ===== */
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
}

/* ===== 动态背景层 ===== */
.background-layer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  background: var(--bg-primary);
  transition: background 0.5s ease;
}

.grid-pattern {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image:
    linear-gradient(var(--border-color) 1px, transparent 1px),
    linear-gradient(90deg, var(--border-color) 1px, transparent 1px);
  background-size: 60px 60px;
  opacity: 0.5;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  animation: float 20s ease-in-out infinite;
}

.orb-1 {
  width: 600px;
  height: 600px;
  background: var(--orb-1);
  top: -200px;
  right: -100px;
  animation-delay: 0s;
}

.orb-2 {
  width: 500px;
  height: 500px;
  background: var(--orb-2);
  bottom: -150px;
  left: -100px;
  animation-delay: -7s;
}

.orb-3 {
  width: 400px;
  height: 400px;
  background: var(--orb-3);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: -14s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(30px, -30px) scale(1.05);
  }
  50% {
    transform: translate(-20px, 20px) scale(0.95);
  }
  75% {
    transform: translate(-30px, -20px) scale(1.02);
  }
}

/* ===== 磨砂玻璃导航栏 ===== */
.glass-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--glass-border);
  transition: all 0.3s ease;
}

.header-content {
  max-width: 1600px;
  margin: 0 auto;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
}

/* Logo */
.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.02);
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: var(--primary-gradient);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.logo-icon svg {
  width: 24px;
  height: 24px;
}

.logo .title {
  font-size: 18px;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 导航中心 */
.nav-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 30px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 12px;
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s ease;
}

.nav-item svg {
  width: 18px;
  height: 18px;
}

.nav-item:hover {
  color: var(--text-primary);
  background: var(--glass-bg);
}

.nav-item.active {
  color: white;
  background: var(--primary-gradient);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

/* 面包屑 */
.breadcrumb {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.crumb {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: var(--text-secondary);
}

.crumb a {
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.3s ease;
}

.crumb a:hover {
  color: var(--text-primary);
}

.crumb-separator {
  width: 14px;
  height: 14px;
  margin: 0 8px;
  color: var(--text-muted);
}

/* 右侧区域 */
.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

/* 统计玻璃卡片 */
.stats-glass {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-sm);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-highlight {
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-divider {
  width: 1px;
  height: 30px;
  background: var(--border-color);
}

/* 主题切换按钮 */
.theme-toggle {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  border: 1px solid var(--border-color);
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: all 0.3s ease;
}

.theme-toggle:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
  transform: scale(1.05);
}

.theme-toggle svg {
  width: 20px;
  height: 20px;
}

/* ===== 主内容区域 ===== */
.main-content {
  flex: 1;
  padding: 30px;
  max-width: 1600px;
  width: 100%;
  margin: 0 auto;
}

/* ===== 页面切换动画 ===== */
.page-enter-active,
.page-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* ===== 底部 ===== */
.glass-footer {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border-top: 1px solid var(--glass-border);
}

.footer-content {
  max-width: 1600px;
  margin: 0 auto;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  color: var(--text-muted);
  font-size: 14px;
}

.footer-divider {
  color: var(--border-color);
}

/* ===== 响应式 ===== */
@media (max-width: 1024px) {
  .nav-center {
    gap: 15px;
  }

  .stats-glass {
    display: none;
  }
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 20px;
  }

  .nav-item span {
    display: none;
  }

  .breadcrumb {
    display: none;
  }

  .main-content {
    padding: 20px;
  }
}

</style>

<style scoped>
/* ===== 全局样式覆盖（组件内） ===== */
:deep(.el-card) {
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-md);
  border-radius: 20px;
  transition: all 0.3s ease;
}

:deep(.el-card:hover) {
  box-shadow: var(--shadow-lg);
}

:deep(.el-button--primary) {
  background: var(--primary-gradient);
  border: none;
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
}

:deep(.el-button--primary:hover) {
  background: var(--primary-gradient-hover);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

:deep(.el-dialog) {
  background: var(--bg-elevated);
  border-radius: 24px;
  border: 1px solid var(--border-color);
}
</style>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Element Plus 暗黑模式适配 */
.dark-mode {
  color-scheme: dark;
}

.dark-mode :deep(.el-input__wrapper) {
  background: var(--bg-secondary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.dark-mode :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--glass-border) inset;
}

.dark-mode :deep(.el-input__inner) {
  color: var(--text-primary);
}

.dark-mode :deep(.el-textarea__inner) {
  background: var(--bg-secondary);
  border-color: var(--border-color);
  color: var(--text-primary);
}

.dark-mode :deep(.el-table) {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.dark-mode :deep(.el-table th) {
  background: var(--bg-elevated);
  color: var(--text-secondary);
}

.dark-mode :deep(.el-table tr) {
  background: var(--bg-secondary);
}

.dark-mode :deep(.el-table td) {
  border-color: var(--border-color);
}

.dark-mode :deep(.el-table--enable-row-hover .el-table__body tr:hover > td) {
  background: var(--bg-elevated);
}

.dark-mode :deep(.el-tag) {
  background: var(--bg-elevated);
  border-color: var(--border-color);
  color: var(--text-primary);
}

.dark-mode :deep(.el-timeline-item__timestamp) {
  color: var(--text-secondary);
}

.dark-mode :deep(.el-empty__description) {
  color: var(--text-secondary);
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}

.dark-mode ::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.2);
}

.dark-mode ::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.4);
}
</style>
