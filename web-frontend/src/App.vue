<template>
  <el-config-provider :locale="zhCn">
    <div id="app">
      <!-- 顶部导航栏 -->
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo" @click="$router.push('/')">
            <el-icon :size="24"><Monitor /></el-icon>
            <span class="title">服务器巡检报告系统</span>
          </div>
          
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path" :to="item.path">
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
          
          <div class="stats" v-if="stats">
            <el-tag>项目: {{ stats.total_projects }}</el-tag>
            <el-tag type="success">主机: {{ stats.total_hosts }}</el-tag>
          </div>
        </div>
      </el-header>
      
      <!-- 主内容区域 -->
      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
      
      <!-- 底部 -->
      <el-footer class="app-footer">
        <div>© 2026 服务器巡检报告系统</div>
      </el-footer>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getStats } from '@/api/project'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

const route = useRoute()
const stats = ref(null)

// 面包屑导航
const breadcrumbs = computed(() => {
  const crumbs = [{ title: '项目列表', path: '/' }]
  
  if (route.params.projectCode) {
    crumbs.push({
      title: decodeURIComponent(route.params.projectCode),
      path: `/projects/${route.params.projectCode}`
    })
  }
  
  if (route.params.hostname) {
    crumbs.push({
      title: decodeURIComponent(route.params.hostname),
      path: route.path
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

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  height: 60px !important;
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 18px;
  font-weight: 600;
  color: #409eff;
}

.logo:hover {
  opacity: 0.8;
}

.breadcrumb {
  flex: 1;
  margin: 0 40px;
}

.stats {
  display: flex;
  gap: 10px;
}

.app-main {
  flex: 1;
  background: #f5f7fa;
  padding: 20px;
}

.app-footer {
  background: #fff;
  border-top: 1px solid #e4e7ed;
  text-align: center;
  color: #909399;
  font-size: 14px;
  height: 50px !important;
  line-height: 50px;
  padding: 0;
}

/* 页面切换动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
}
</style>
