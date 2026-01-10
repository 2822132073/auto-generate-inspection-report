<template>
  <div class="project-list">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <span class="title-icon">dashboard</span>
          项目列表
        </h1>
        <div class="stats-row" v-if="stats">
          <div class="stat-card">
            <div class="stat-icon stat-blue">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_projects }}</span>
              <span class="stat-label">项目总数</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon stat-purple">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                <line x1="8" y1="21" x2="16" y2="21"/>
                <line x1="12" y1="17" x2="12" y2="21"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_hosts }}</span>
              <span class="stat-label">主机总数</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon stat-green">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_inspections }}</span>
              <span class="stat-label">巡检记录</span>
            </div>
          </div>
        </div>
      </div>
      <button class="create-btn" @click="showCreateDialog = true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        <span>创建项目</span>
      </button>
    </header>

    <!-- 骨架屏加载 -->
    <div v-if="loading" class="skeleton-grid">
      <div v-for="i in 6" :key="i" class="skeleton-card">
        <div class="skeleton-header">
          <div class="skeleton-icon"></div>
          <div class="skeleton-tag"></div>
        </div>
        <div class="skeleton-title"></div>
        <div class="skeleton-text"></div>
        <div class="skeleton-text short"></div>
        <div class="skeleton-footer">
          <div class="skeleton-stat"></div>
          <div class="skeleton-stat"></div>
        </div>
      </div>
    </div>

    <!-- 项目卡片网格 -->
    <transition-group v-else-if="projects.length > 0" tag="div" name="card" class="project-grid">
      <div
        v-for="(project, index) in projects"
        :key="project.id"
        class="project-card"
        :style="{ animationDelay: `${index * 0.05}s` }"
        @click="goToProject(project)"
      >
        <div class="card-glow"></div>
        <div class="card-inner">
          <div class="card-header">
            <div class="project-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
              </svg>
            </div>
            <div class="status-badge" :class="project.status">
              <span class="status-dot"></span>
              {{ project.status === 'active' ? '活跃' : '归档' }}
            </div>
          </div>

          <div class="card-content">
            <h3 class="project-code">{{ project.project_code }}</h3>
            <p class="project-name">{{ project.project_name }}</p>
            <p class="project-desc">{{ truncateText(project.description, 80) }}</p>

            <div class="project-stats">
              <div class="stat">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                  <line x1="8" y1="21" x2="16" y2="21"/>
                  <line x1="12" y1="17" x2="12" y2="21"/>
                </svg>
                <span>{{ getProjectHostCount(project.project_code) }} 台主机</span>
              </div>
              <div class="stat">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
                <span>{{ formatDate(project.created_at) }}</span>
              </div>
            </div>
          </div>

          <div class="card-arrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </div>
        </div>
      </div>
    </transition-group>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-illustration">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          <circle cx="12" cy="12" r="3"/>
          <path d="M12 9v6M9 12h6"/>
        </svg>
      </div>
      <h3>暂无项目数据</h3>
      <p>请通过 API 提交巡检数据创建项目</p>
      <button class="refresh-btn" @click="refresh">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="23 4 23 10 17 10"/>
          <polyline points="1 20 1 14 7 14"/>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
        </svg>
        刷新
      </button>
    </div>

    <!-- 创建项目对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title=""
      width="480px"
      @close="resetForm"
      class="create-dialog"
      :show-close="false"
    >
      <div class="dialog-header">
        <div class="dialog-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
        </div>
        <h2>创建新项目</h2>
        <p>填写项目信息以开始监控服务器</p>
      </div>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-position="top"
        class="create-form"
      >
        <el-form-item label="项目代码" prop="project_code">
          <el-input
            v-model="formData.project_code"
            placeholder="例如: PRJ001"
            size="large"
            clearable
          />
        </el-form-item>
        <el-form-item label="项目名称" prop="project_name">
          <el-input
            v-model="formData.project_name"
            placeholder="例如: 生产环境监控"
            size="large"
            clearable
          />
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="描述该项目的主要用途（可选）"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false" size="large">取消</el-button>
          <el-button type="primary" @click="handleCreate" :loading="creating" size="large">
            创建项目
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProjects, getStats, createProject, getProjectHosts } from '@/api/project'
import { formatDate } from '@/utils/date'
import { truncateText } from '@/utils/format'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const projects = ref([])
const stats = ref(null)
const hostCounts = ref({})

// 创建项目相关状态
const showCreateDialog = ref(false)
const creating = ref(false)
const formRef = ref(null)
const formData = ref({
  project_code: '',
  project_name: '',
  description: ''
})

// 表单验证规则
const formRules = {
  project_code: [
    { required: true, message: '请输入项目代码', trigger: 'blur' },
    { min: 2, max: 50, message: '项目代码长度为 2-50 个字符', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9_-]+$/, message: '项目代码只能包含字母、数字、下划线和短横线', trigger: 'blur' }
  ],
  project_name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 100, message: '项目名称长度为 2-100 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '项目描述最多 500 个字符', trigger: 'blur' }
  ]
}

// 获取项目列表
const fetchProjects = async () => {
  loading.value = true
  try {
    const res = await getProjects({ status: 'all' })
    projects.value = res.data.projects || []

    // 获取每个项目的主机数量
    for (const project of projects.value) {
      try {
        const hostsRes = await getProjectHosts(project.project_code)
        hostCounts.value[project.project_code] = hostsRes.data.host_count || 0
      } catch (error) {
        hostCounts.value[project.project_code] = 0
      }
    }
  } catch (error) {
    console.error('获取项目列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取统计信息
const fetchStats = async () => {
  try {
    const res = await getStats()
    stats.value = res.data
  } catch (error) {
    console.error('获取统计信息失败:', error)
  }
}

// 获取项目主机数
const getProjectHostCount = (projectCode) => {
  return hostCounts.value[projectCode] || 0
}

// 跳转到项目详情
const goToProject = (project) => {
  router.push(`/projects/${project.project_code}`)
}

// 刷新
const refresh = () => {
  fetchProjects()
  fetchStats()
}

// 重置表单
const resetForm = () => {
  formData.value = {
    project_code: '',
    project_name: '',
    description: ''
  }
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

// 创建项目
const handleCreate = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    creating.value = true
    await createProject(formData.value)
    ElMessage.success('项目创建成功！')
    showCreateDialog.value = false
    resetForm()
    refresh()
  } catch (error) {
    if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error)
    } else if (error.message) {
      console.log('表单验证失败')
    } else {
      ElMessage.error('创建项目失败，请稍后重试')
    }
  } finally {
    creating.value = false
  }
}

onMounted(() => {
  fetchProjects()
  fetchStats()
})
</script>

<style scoped>
.project-list {
  max-width: 1600px;
  margin: 0 auto;
}

/* ===== 页面头部 ===== */
.page-header {
  margin-bottom: 40px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 30px;
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  font-family: 'Space Grotesk', 'Inter', sans-serif;
  font-size: 28px;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 统计卡片行 */
.stats-row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
  min-width: 180px;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon svg {
  width: 28px;
  height: 28px;
  stroke-width: 2.5;
}

.stat-blue {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-purple {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-green {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 2px;
}

/* 创建按钮 */
.create-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 28px;
  background: var(--primary-gradient);
  border: none;
  border-radius: 16px;
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.create-btn svg {
  width: 20px;
  height: 20px;
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
}

.create-btn:active {
  transform: translateY(0);
}

/* ===== 骨架屏 ===== */
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 24px;
}

.skeleton-card {
  background: var(--bg-elevated);
  border-radius: 24px;
  padding: 24px;
  border: 1px solid var(--border-color);
}

.skeleton-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.skeleton-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(90deg, var(--bg-secondary) 25%, var(--bg-primary) 50%, var(--bg-secondary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-tag {
  width: 60px;
  height: 24px;
  border-radius: 8px;
  background: linear-gradient(90deg, var(--bg-secondary) 25%, var(--bg-primary) 50%, var(--bg-secondary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-title {
  width: 70%;
  height: 24px;
  border-radius: 8px;
  background: linear-gradient(90deg, var(--bg-secondary) 25%, var(--bg-primary) 50%, var(--bg-secondary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  margin-bottom: 12px;
}

.skeleton-text {
  width: 90%;
  height: 16px;
  border-radius: 6px;
  background: linear-gradient(90deg, var(--bg-secondary) 25%, var(--bg-primary) 50%, var(--bg-secondary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  margin-bottom: 8px;
}

.skeleton-text.short {
  width: 60%;
}

.skeleton-footer {
  display: flex;
  gap: 20px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.skeleton-stat {
  flex: 1;
  height: 16px;
  border-radius: 6px;
  background: linear-gradient(90deg, var(--bg-secondary) 25%, var(--bg-primary) 50%, var(--bg-secondary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* ===== 项目卡片网格 ===== */
.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 24px;
}

.project-card {
  position: relative;
  cursor: pointer;
  animation: fadeInUp 0.5s ease-out backwards;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-glow {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: var(--primary-gradient);
  border-radius: 26px;
  opacity: 0;
  transition: opacity 0.3s ease;
  filter: blur(15px);
  z-index: -1;
}

.project-card:hover .card-glow {
  opacity: 0.4;
}

.card-inner {
  background: var(--bg-elevated);
  border-radius: 24px;
  padding: 24px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-md);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.project-card:hover .card-inner {
  transform: translateY(-8px);
  box-shadow: var(--shadow-lg);
  border-color: transparent;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.project-icon {
  width: 52px;
  height: 52px;
  background: var(--primary-gradient);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.project-icon svg {
  width: 26px;
  height: 26px;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  background: var(--bg-primary);
  color: var(--text-secondary);
  transition: all 0.3s ease;
}

.status-badge.active {
  background: rgba(79, 172, 254, 0.15);
  color: #4facfe;
}

.status-badge.archived {
  background: var(--bg-primary);
  color: var(--text-muted);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s ease-in-out infinite;
}

.status-badge.archived .status-dot {
  animation: none;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}

.card-content {
  margin-bottom: 20px;
}

.project-code {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
  letter-spacing: -0.5px;
}

.project-name {
  font-size: 15px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.project-desc {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.6;
  min-height: 40px;
  margin-bottom: 20px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.project-stats {
  display: flex;
  justify-content: space-between;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.stat {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-muted);
}

.stat svg {
  width: 16px;
  height: 16px;
  opacity: 0.6;
}

.card-arrow {
  position: absolute;
  top: 50%;
  right: 16px;
  transform: translateY(-50%) translateX(10px);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-muted);
  transition: all 0.3s ease;
  opacity: 0;
  pointer-events: none;
}

.project-card:hover .card-arrow {
  opacity: 1;
  transform: translateY(-50%) translateX(0);
}

.card-arrow svg {
  width: 18px;
  height: 18px;
}

/* ===== 卡片动画 ===== */
.card-enter-active {
  transition: all 0.5s ease;
}

.card-enter-from {
  opacity: 0;
  transform: scale(0.9) translateY(20px);
}

.card-enter-to {
  opacity: 1;
  transform: scale(1) translateY(0);
}

/* ===== 空状态 ===== */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-illustration {
  width: 120px;
  height: 120px;
  margin: 0 auto 30px;
  background: var(--glass-bg);
  border-radius: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.empty-illustration svg {
  width: 60px;
  height: 60px;
}

.empty-state h3 {
  font-size: 20px;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-state p {
  color: var(--text-muted);
  margin-bottom: 24px;
}

.refresh-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--glass-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn svg {
  width: 16px;
  height: 16px;
}

.refresh-btn:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border-color: var(--glass-border);
}

/* ===== 创建对话框 ===== */
:deep(.create-dialog) {
  background: var(--bg-elevated);
}

:deep(.create-dialog .el-dialog__header) {
  display: none;
}

:deep(.create-dialog .el-dialog__body) {
  padding: 40px;
}

:deep(.create-dialog .el-dialog__footer) {
  padding: 0 40px 30px;
}

.dialog-header {
  text-align: center;
  margin-bottom: 30px;
}

.dialog-icon {
  width: 64px;
  height: 64px;
  background: var(--primary-gradient);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin: 0 auto 20px;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.dialog-icon svg {
  width: 32px;
  height: 32px;
}

.dialog-header h2 {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.dialog-header p {
  color: var(--text-muted);
  font-size: 14px;
}

.create-form :deep(.el-form-item__label) {
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 14px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* ===== 响应式 ===== */
@media (max-width: 1024px) {
  .project-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
  }

  .stats-row {
    width: 100%;
  }

  .stat-card {
    flex: 1;
    min-width: 140px;
  }

  .project-grid {
    grid-template-columns: 1fr;
  }

  .create-btn span {
    display: none;
  }
}
</style>
