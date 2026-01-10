<template>
  <div class="project-list">
    <div class="page-header">
      <div class="header-left">
        <h1>项目列表</h1>
        <div class="header-stats" v-if="stats">
          <el-statistic title="项目总数" :value="stats.total_projects" />
          <el-statistic title="主机总数" :value="stats.total_hosts" />
          <el-statistic title="巡检记录" :value="stats.total_inspections" />
        </div>
      </div>
      <el-button type="primary" @click="showCreateDialog = true" size="large">
        <el-icon><Plus /></el-icon>
        创建项目
      </el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="3" animated />
    </div>

    <!-- 项目卡片网格 -->
    <div v-else-if="projects.length > 0" class="project-grid">
      <el-card
        v-for="project in projects"
        :key="project.id"
        class="project-card"
        shadow="hover"
        @click="goToProject(project)"
      >
        <template #header>
          <div class="card-header">
            <el-icon :size="32" color="#409eff"><FolderOpened /></el-icon>
            <el-tag v-if="project.status === 'active'" type="success" size="small">活跃</el-tag>
            <el-tag v-else type="info" size="small">归档</el-tag>
          </div>
        </template>

        <div class="card-content">
          <h3 class="project-code">{{ project.project_code }}</h3>
          <p class="project-name">{{ project.project_name }}</p>
          <p class="project-desc">{{ truncateText(project.description, 100) }}</p>
          
          <div class="project-stats">
            <div class="stat-item">
              <el-icon><Monitor /></el-icon>
              <span>{{ getProjectHostCount(project.project_code) }} 台主机</span>
            </div>
            <div class="stat-item">
              <el-icon><Clock /></el-icon>
              <span>{{ formatDate(project.created_at) }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-else
      description="暂无项目数据，请通过 API 提交巡检数据"
      :image-size="200"
    >
      <el-button type="primary" @click="refresh">刷新</el-button>
    </el-empty>

    <!-- 创建项目对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建新项目"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="项目代码" prop="project_code">
          <el-input
            v-model="formData.project_code"
            placeholder="请输入项目代码，如: PRJ001"
            clearable
          />
        </el-form-item>
        <el-form-item label="项目名称" prop="project_name">
          <el-input
            v-model="formData.project_name"
            placeholder="请输入项目名称"
            clearable
          />
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入项目描述（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="handleCreate" :loading="creating">
            创建
          </el-button>
        </span>
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
        console.error(`获取项目 ${project.project_code} 主机数量失败:`, error)
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
    // 验证表单
    await formRef.value.validate()
    
    creating.value = true
    
    // 提交创建请求
    await createProject(formData.value)
    
    ElMessage.success('项目创建成功！')
    
    // 关闭对话框
    showCreateDialog.value = false
    
    // 重置表单
    resetForm()
    
    // 刷新列表
    refresh()
  } catch (error) {
    if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error)
    } else if (error.message) {
      // 表单验证错误，不显示消息
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
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-left {
  flex: 1;
}

.page-header h1 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 20px;
}

.header-stats {
  display: flex;
  gap: 40px;
}

.loading-container {
  padding: 40px;
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.project-card {
  cursor: pointer;
  transition: all 0.3s;
}

.project-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-content {
  padding-top: 10px;
}

.project-code {
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 8px;
}

.project-name {
  font-size: 16px;
  color: #606266;
  margin-bottom: 12px;
}

.project-desc {
  font-size: 14px;
  color: #909399;
  line-height: 1.5;
  min-height: 42px;
  margin-bottom: 16px;
}

.project-stats {
  display: flex;
  justify-content: space-between;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #909399;
}

@media (max-width: 768px) {
  .project-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
}
</style>
