<template>
  <div class="project-detail">
    <!-- 返回按钮 -->
    <button class="back-btn" @click="$router.push('/')">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="15 18 9 12 15 6"/>
      </svg>
      <span>返回列表</span>
    </button>

    <!-- 项目信息卡片 -->
    <div class="info-card" v-loading="loading">
      <div class="info-header">
        <div class="info-main">
          <div class="project-banner">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <div>
            <h1 class="project-title">{{ projectInfo?.project_name || projectCode }}</h1>
            <p class="project-code-tag">{{ projectCode }}</p>
          </div>
        </div>
        <div class="action-buttons">
          <button class="action-btn secondary" @click="showDeployDialog = true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
            <span>部署命令</span>
          </button>
          <button class="action-btn primary" @click="showReportDialog = true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
            <span>生成报告</span>
          </button>
        </div>
      </div>

      <p class="project-description" v-if="projectInfo?.description">
        {{ projectInfo.description }}
      </p>

      <!-- 统计数据 -->
      <div class="stats-grid" v-if="statistics">
        <div class="stat-box">
          <div class="stat-icon-box blue">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
              <line x1="8" y1="21" x2="16" y2="21"/>
              <line x1="12" y1="17" x2="12" y2="21"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-number">{{ statistics.total_hosts }}</span>
            <span class="stat-text">主机数量</span>
          </div>
        </div>
        <div class="stat-box">
          <div class="stat-icon-box purple">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-number">{{ statistics.total_inspections }}</span>
            <span class="stat-text">巡检次数</span>
          </div>
        </div>
        <div class="stat-box">
          <div class="stat-icon-box green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-number">{{ formatRelativeTime(statistics.latest_inspection) }}</span>
            <span class="stat-text">最新巡检</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 主机列表 -->
    <div class="hosts-section">
      <div class="section-header">
        <h2 class="section-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
            <line x1="8" y1="21" x2="16" y2="21"/>
            <line x1="12" y1="17" x2="12" y2="21"/>
          </svg>
          主机列表
        </h2>
        <span class="section-count">共 {{ hosts.length }} 台</span>
      </div>

      <div v-if="hostsLoading" class="skeleton-hosts">
        <div v-for="i in 4" :key="i" class="skeleton-host-card">
          <div class="skeleton-host-icon"></div>
          <div class="skeleton-host-info">
            <div class="skeleton-line"></div>
            <div class="skeleton-line short"></div>
          </div>
        </div>
      </div>

      <div v-else-if="hosts.length > 0" class="hosts-grid">
        <div
          v-for="(host, index) in hosts"
          :key="host.hostname"
          class="host-card"
          :style="{ animationDelay: `${index * 0.05}s` }"
          @click="goToHost(host)"
        >
          <div class="host-card-inner">
            <div class="host-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                <line x1="8" y1="21" x2="16" y2="21"/>
                <line x1="12" y1="17" x2="12" y2="21"/>
              </svg>
            </div>

            <div class="host-content">
              <h3 class="host-name">{{ host.hostname }}</h3>
              <p class="host-ip">{{ host.ip }}</p>

              <div class="host-tags">
                <span class="host-tag">{{ host.os }}</span>
                <span class="host-tag">{{ host.arch }}</span>
              </div>

              <div class="host-meta">
                <div class="meta-item">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                  </svg>
                  <span>{{ formatRelativeTime(host.timestamp) }}</span>
                </div>
                <div class="meta-item">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                  </svg>
                  <span>{{ hostInspectionCounts[host.hostname] || 0 }} 次巡检</span>
                </div>
              </div>
            </div>

            <div class="host-arrow">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="empty-hosts">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
            <line x1="8" y1="21" x2="16" y2="21"/>
            <line x1="12" y1="17" x2="12" y2="21"/>
            <circle cx="12" cy="10" r="2"/>
          </svg>
        </div>
        <h3>该项目暂无主机数据</h3>
        <p>请通过 API 提交巡检数据以添加主机</p>
      </div>
    </div>

    <!-- 报告生成对话框 -->
    <el-dialog
      v-model="showReportDialog"
      title=""
      width="500px"
      :close-on-click-modal="false"
      class="report-dialog"
      :show-close="false"
    >
      <div class="dialog-header">
        <div class="dialog-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
        </div>
        <h2>生成项目巡检报告</h2>
        <p>汇总所有主机的最新巡检数据</p>
      </div>

      <div class="report-info">
        <div class="info-row">
          <span class="label">项目名称</span>
          <span class="value">{{ projectInfo?.project_name }}</span>
        </div>
        <div class="info-row">
          <span class="label">主机数量</span>
          <span class="value">{{ hosts.length }} 台</span>
        </div>
      </div>

      <el-form :model="reportForm" label-position="top" class="report-form">
        <el-form-item label="报告标题">
          <el-input v-model="reportForm.title" placeholder="请输入报告标题" size="large" />
        </el-form-item>
      </el-form>

      <div v-if="selectedTemplate" class="template-notice">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="16" x2="12" y2="12"/>
          <line x1="12" y1="8" x2="12.01" y2="8"/>
        </svg>
        <span>使用模板: {{ selectedTemplate.name }}</span>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showReportDialog = false" size="large">取消</el-button>
          <el-button type="primary" @click="handleGenerateReport" :loading="generating" size="large">
            生成报告
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 报告生成成功对话框 -->
    <el-dialog
      v-model="showSuccessDialog"
      title=""
      width="400px"
      class="success-dialog"
      :show-close="false"
    >
      <div class="success-content">
        <div class="success-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>
        <h3>报告生成成功！</h3>
        <p>文件大小: {{ formatFileSize(reportInfo?.file_size) }}</p>
        <button class="download-btn" @click="handleDownloadReport">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          立即下载
        </button>
      </div>
    </el-dialog>

    <!-- 部署命令对话框 -->
    <el-dialog
      v-model="showDeployDialog"
      title=""
      width="650px"
      class="deploy-dialog"
      :show-close="false"
    >
      <div class="dialog-header">
        <div class="dialog-icon terminal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="4 17 10 11 4 5"/>
            <line x1="12" y1="19" x2="20" y2="19"/>
          </svg>
        </div>
        <h2>部署命令</h2>
        <p>在目标服务器上执行以下命令</p>
      </div>

      <p class="deploy-tip">
        将自动部署巡检脚本并设置定时任务（每天凌晨2点执行）
      </p>

      <div class="deploy-command-box">
        <pre class="deploy-command">{{ deployCommand }}</pre>
        <button class="copy-btn" @click="copyDeployCommand">
          <svg v-if="!copied" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          {{ copied ? '已复制' : '复制命令' }}
        </button>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showDeployDialog = false; copied = false" size="large">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getProjectByCode, getProjectStatistics, getProjectHosts } from '@/api/project'
import { getTemplates, generateReport, downloadReport } from '@/api/report'
import { getInspections } from '@/api/inspection'
import { formatRelativeTime } from '@/utils/date'
import { formatFileSize } from '@/utils/format'

const router = useRouter()
const route = useRoute()
const projectCode = route.params.projectCode

const loading = ref(false)
const hostsLoading = ref(false)
const projectInfo = ref(null)
const statistics = ref(null)
const hosts = ref([])
const hostInspectionCounts = ref({})

// 报告相关
const showReportDialog = ref(false)
const showSuccessDialog = ref(false)
const showDeployDialog = ref(false)
const templates = ref([])
const generating = ref(false)
const reportInfo = ref(null)
const copied = ref(false)
const reportForm = ref({
  title: `服务器巡检报告 - ${projectCode}`,
  templateId: null
})

// 获取项目信息
const fetchProjectInfo = async () => {
  loading.value = true
  try {
    const res = await getProjectByCode(projectCode)
    projectInfo.value = res.data
    reportForm.value.title = `服务器巡检报告 - ${res.data.project_name}`
  } catch (error) {
    console.error('获取项目信息失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取项目统计
const fetchStatistics = async () => {
  try {
    if (projectInfo.value?.id) {
      const res = await getProjectStatistics(projectInfo.value.id)
      statistics.value = res.data.statistics
    }
  } catch (error) {
    console.error('获取统计信息失败:', error)
  }
}

// 获取主机列表
const fetchHosts = async () => {
  hostsLoading.value = true
  try {
    if (projectInfo.value?.id) {
      const res = await getProjectHosts(projectInfo.value.id)
      hosts.value = res.data.hosts || []

      for (const host of hosts.value) {
        await fetchHostInspectionCount(host.hostname)
      }
    }
  } catch (error) {
    console.error('获取主机列表失败:', error)
  } finally {
    hostsLoading.value = false
  }
}

// 获取主机巡检次数
const fetchHostInspectionCount = async (hostname) => {
  try {
    const res = await getInspections({
      hostname,
      project_id: projectCode,
      page: 1,
      page_size: 1
    })
    hostInspectionCounts.value[hostname] = res.data?.total || 0
  } catch (error) {
    hostInspectionCounts.value[hostname] = 0
  }
}

// 获取模板列表
const fetchTemplates = async () => {
  try {
    const res = await getTemplates()
    templates.value = res.data.templates || []

    const defaultTemplate = templates.value.find(t => t.is_default)
    if (defaultTemplate) {
      reportForm.value.templateId = defaultTemplate.id
    } else if (templates.value.length > 0) {
      reportForm.value.templateId = templates.value[0].id
    }
  } catch (error) {
    console.error('获取模板列表失败:', error)
  }
}

// 计算当前选中的模板
const selectedTemplate = computed(() => {
  return templates.value.find(t => t.id === reportForm.value.templateId)
})

// 计算部署命令
const deployCommand = computed(() => {
  // 获取后端服务器地址（从环境变量或前端地址推导）
  const apiBase = import.meta.env.VITE_API_BASE_URL || '/api/v1'
  let serverUrl
  if (apiBase.startsWith('http')) {
    // 完整 URL，如 http://localhost:8000/api/v1
    serverUrl = apiBase.replace(/\/api\/v\d+$/, '')
  } else {
    // 相对路径，使用前端 origin
    serverUrl = window.location.origin
  }
  const code = projectInfo.value?.project_code || projectCode
  return `# 下载巡检脚本
curl -o /usr/local/bin/get_system_info.sh ${serverUrl}/static/get_system_info.sh
chmod +x /usr/local/bin/get_system_info.sh

# 添加 cron 任务（每天凌晨2点执行）
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/get_system_info.sh ${serverUrl} ${code}") | crontab -`
})

// 复制部署命令
const copyDeployCommand = async () => {
  try {
    await navigator.clipboard.writeText(deployCommand.value)
    copied.value = true
    ElMessage.success('部署命令已复制到剪贴板')
    setTimeout(() => {
      showDeployDialog.value = false
      copied.value = false
    }, 1000)
  } catch (err) {
    ElMessage.error('复制失败，请手动复制')
  }
}

// 生成报告
const handleGenerateReport = async () => {
  if (!reportForm.value.templateId) {
    ElMessage.warning('请选择报告模板')
    return
  }

  generating.value = true
  try {
    const res = await generateReport(projectInfo.value.id, {
      options: {
        title: reportForm.value.title,
        template_id: reportForm.value.templateId
      }
    })

    reportInfo.value = res.data
    showReportDialog.value = false
    showSuccessDialog.value = true
    ElMessage.success('报告生成成功')
  } catch (error) {
    console.error('生成报告失败:', error)
  } finally {
    generating.value = false
  }
}

// 下载报告
const handleDownloadReport = async () => {
  try {
    const response = await downloadReport(projectInfo.value.id)
    const filename = `${projectCode}_${Date.now()}.docx`
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    showSuccessDialog.value = false
    ElMessage.success('报告下载成功')
  } catch (error) {
    console.error('下载报告失败:', error)
  }
}

// 跳转到主机详情
const goToHost = (host) => {
  router.push(`/projects/${projectCode}/hosts/${host.hostname}`)
}

onMounted(async () => {
  await fetchProjectInfo()
  await fetchStatistics()
  await fetchHosts()
  await fetchTemplates()
})
</script>

<style scoped>
.project-detail {
  max-width: 1400px;
  margin: 0 auto;
}

/* ===== 返回按钮 ===== */
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 24px;
}

.back-btn svg {
  width: 18px;
  height: 18px;
}

.back-btn:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
  transform: translateX(-3px);
}

/* ===== 信息卡片 ===== */
.info-card {
  background: var(--bg-elevated);
  border-radius: 24px;
  padding: 32px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-md);
  margin-bottom: 32px;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 30px;
  margin-bottom: 24px;
}

.info-main {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
}

.project-banner {
  width: 80px;
  height: 80px;
  background: var(--primary-gradient);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.project-banner svg {
  width: 40px;
  height: 40px;
}

.project-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.project-code-tag {
  display: inline-block;
  padding: 6px 14px;
  background: var(--bg-primary);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 24px;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.action-btn svg {
  width: 18px;
  height: 18px;
}

.action-btn.primary {
  background: var(--primary-gradient);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.action-btn.secondary {
  background: var(--bg-primary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.action-btn.secondary:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.project-description {
  color: var(--text-secondary);
  line-height: 1.7;
  font-size: 15px;
  margin-bottom: 28px;
  padding: 20px;
  background: var(--bg-primary);
  border-radius: 16px;
}

/* ===== 统计网格 ===== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.stat-box {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid var(--glass-border);
  transition: all 0.3s ease;
}

.stat-box:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.stat-icon-box {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon-box svg {
  width: 22px;
  height: 22px;
}

.stat-icon-box.blue {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon-box.purple {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon-box.green {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-text {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 2px;
}

/* ===== 主机区域 ===== */
.hosts-section {
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.section-title svg {
  width: 26px;
  height: 26px;
  color: #667eea;
}

.section-count {
  padding: 8px 16px;
  background: var(--glass-bg);
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-muted);
}

/* ===== 主机骨架屏 ===== */
.skeleton-hosts {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.skeleton-host-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: var(--bg-elevated);
  border-radius: 20px;
  border: 1px solid var(--border-color);
}

.skeleton-host-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(90deg, var(--bg-secondary) 25%, var(--bg-primary) 50%, var(--bg-secondary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-host-info {
  flex: 1;
}

.skeleton-line {
  height: 16px;
  border-radius: 6px;
  background: linear-gradient(90deg, var(--bg-secondary) 25%, var(--bg-primary) 50%, var(--bg-secondary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  margin-bottom: 8px;
}

.skeleton-line.short {
  width: 60%;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ===== 主机卡片网格 ===== */
.hosts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.host-card {
  animation: fadeInUp 0.5s ease-out backwards;
  cursor: pointer;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.host-card-inner {
  background: var(--bg-elevated);
  border-radius: 20px;
  padding: 24px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  position: relative;
  overflow: hidden;
}

.host-card-inner::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--primary-gradient);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.host-card:hover .host-card-inner {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

.host-card:hover .host-card-inner::before {
  opacity: 1;
}

.host-icon {
  width: 48px;
  height: 48px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #667eea;
  flex-shrink: 0;
}

.host-icon svg {
  width: 24px;
  height: 24px;
}

.host-content {
  flex: 1;
}

.host-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.host-ip {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 12px;
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
}

.host-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.host-tag {
  padding: 4px 10px;
  background: var(--bg-primary);
  border-radius: 6px;
  font-size: 12px;
  color: var(--text-secondary);
}

.host-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-muted);
}

.meta-item svg {
  width: 14px;
  height: 14px;
  opacity: 0.6;
}

.host-arrow {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-muted);
  transition: all 0.3s ease;
  opacity: 0;
  transform: translateX(-8px);
  flex-shrink: 0;
}

.host-card:hover .host-arrow {
  opacity: 1;
  transform: translateX(0);
}

.host-arrow svg {
  width: 16px;
  height: 16px;
}

/* ===== 空状态 ===== */
.empty-hosts {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  width: 100px;
  height: 100px;
  margin: 0 auto 20px;
  background: var(--glass-bg);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.empty-icon svg {
  width: 50px;
  height: 50px;
}

.empty-hosts h3 {
  font-size: 18px;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-hosts p {
  color: var(--text-muted);
  font-size: 14px;
}

/* ===== 对话框样式 ===== */
:deep(.report-dialog),
:deep(.deploy-dialog) {
  background: var(--bg-elevated);
}

:deep(.report-dialog .el-dialog__header),
:deep(.deploy-dialog .el-dialog__header) {
  display: none;
}

:deep(.report-dialog .el-dialog__body),
:deep(.deploy-dialog .el-dialog__body) {
  padding: 35px;
}

:deep(.report-dialog .el-dialog__footer),
:deep(.deploy-dialog .el-dialog__footer) {
  padding: 0 35px 30px;
}

.dialog-header {
  text-align: center;
  margin-bottom: 25px;
}

.dialog-icon {
  width: 60px;
  height: 60px;
  background: var(--primary-gradient);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin: 0 auto 16px;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.dialog-icon.terminal {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.dialog-icon svg {
  width: 28px;
  height: 28px;
}

.dialog-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.dialog-header p {
  color: var(--text-muted);
  font-size: 14px;
}

/* 报告信息 */
.report-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px;
  background: var(--bg-primary);
  border-radius: 14px;
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-row .label {
  color: var(--text-muted);
  font-size: 14px;
}

.info-row .value {
  color: var(--text-primary);
  font-weight: 500;
}

.report-form :deep(.el-form-item__label) {
  color: var(--text-secondary);
  font-weight: 500;
}

.template-notice {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  color: var(--text-secondary);
  font-size: 14px;
}

.template-notice svg {
  width: 18px;
  height: 18px;
  color: #667eea;
  flex-shrink: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 部署命令 */
.deploy-tip {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 16px;
  line-height: 1.6;
}

.deploy-command-box {
  position: relative;
  background: var(--bg-primary);
  border-radius: 12px;
  overflow: hidden;
}

.deploy-command {
  padding: 20px;
  padding-right: 120px;
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-primary);
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}

.copy-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--primary-gradient);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.copy-btn svg {
  width: 16px;
  height: 16px;
}

.copy-btn:hover {
  transform: scale(1.05);
}

/* 成功对话框 */
:deep(.success-dialog) {
  background: var(--bg-elevated);
}

:deep(.success-dialog .el-dialog__header) {
  display: none;
}

:deep(.success-dialog .el-dialog__body) {
  padding: 40px;
}

:deep(.success-dialog .el-dialog__footer) {
  display: none;
}

.success-content {
  text-align: center;
}

.success-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 8px 25px rgba(79, 172, 254, 0.4);
}

.success-icon svg {
  width: 40px;
  height: 40px;
}

.success-content h3 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.success-content p {
  color: var(--text-muted);
  font-size: 14px;
  margin-bottom: 24px;
}

.download-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 16px;
  background: var(--primary-gradient);
  border: none;
  border-radius: 14px;
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.download-btn svg {
  width: 20px;
  height: 20px;
}

.download-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* ===== 响应式 ===== */
@media (max-width: 1024px) {
  .info-header {
    flex-direction: column;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .info-main {
    flex-direction: column;
    align-items: flex-start;
  }

  .action-buttons {
    width: 100%;
  }

  .action-btn {
    flex: 1;
    justify-content: center;
  }

  .action-btn span {
    display: none;
  }

  .hosts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
