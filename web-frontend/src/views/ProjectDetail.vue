<template>
  <div class="project-detail">
    <!-- 返回按钮 -->
    <el-button @click="$router.push('/')" class="back-btn">
      <el-icon><ArrowLeft /></el-icon>
      返回
    </el-button>

    <!-- 项目信息 -->
    <el-card class="project-info-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <div>
            <h2>{{ projectInfo?.project_name || projectCode }}</h2>
            <p class="project-code">{{ projectCode }}</p>
          </div>
          <div class="header-buttons">
            <el-button type="success" plain @click="showDeployDialog = true">
              <el-icon><DocumentCopy /></el-icon>
              复制部署命令
            </el-button>
            <el-button type="primary" @click="showReportDialog = true">
              <el-icon><Document /></el-icon>
              生成巡检报告
            </el-button>
          </div>
        </div>
      </template>

      <div class="project-description" v-if="projectInfo?.description">
        {{ projectInfo.description }}
      </div>

      <div class="project-statistics" v-if="statistics">
        <el-statistic title="主机数量" :value="statistics.total_hosts" suffix="台" />
        <el-statistic title="巡检次数" :value="statistics.total_inspections" suffix="次" />
        <el-statistic title="最新巡检" :value="formatRelativeTime(statistics.latest_inspection)" />
      </div>
    </el-card>

    <!-- 主机列表 -->
    <div class="hosts-section">
      <h3>主机列表 (共 {{ hosts.length }} 台)</h3>
      
      <div v-if="hostsLoading" class="loading-container">
        <el-skeleton :rows="2" animated />
      </div>

      <div v-else-if="hosts.length > 0" class="hosts-grid">
        <el-card
          v-for="host in hosts"
          :key="host.hostname"
          class="host-card"
          shadow="hover"
          @click="goToHost(host)"
        >
          <div class="host-icon">
            <el-icon :size="32" color="#67c23a"><Monitor /></el-icon>
          </div>
          
          <div class="host-info">
            <h4>{{ host.hostname }}</h4>
            <p class="host-ip">{{ host.ip }}</p>
            
            <div class="host-details">
              <el-tag size="small">{{ host.os }}</el-tag>
              <el-tag size="small" type="info">{{ host.arch }}</el-tag>
            </div>
            
            <div class="host-meta">
              <div class="meta-item">
                <el-icon><Clock /></el-icon>
                <span>{{ formatRelativeTime(host.timestamp) }}</span>
              </div>
              <div class="meta-item">
                <el-icon><Document /></el-icon>
                <span>{{ getHostInspectionCount(host.hostname) }} 次巡检</span>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <el-empty
        v-else
        description="该项目暂无主机数据"
        :image-size="150"
      />
    </div>

    <!-- 报告生成对话框 -->
    <el-dialog
      v-model="showReportDialog"
      title="生成项目巡检报告"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="reportForm" label-width="100px">
        <el-form-item label="项目名称">
          <el-input :value="projectInfo?.project_name" disabled />
        </el-form-item>

        <el-form-item label="主机数量">
          <el-input :value="`${hosts.length} 台`" disabled />
        </el-form-item>

        <el-form-item label="报告标题">
          <el-input v-model="reportForm.title" placeholder="请输入报告标题" />
        </el-form-item>
      </el-form>

      <!-- 移除了模板选择 UI，默认使用简化模板 -->
      <div v-if="selectedTemplate" class="template-info-display">
        <p><strong>使用模板:</strong> {{ selectedTemplate.name }}</p>
        <p class="template-desc-text">{{ selectedTemplate.description }}</p>
      </div>

    <template #footer>
        <el-button @click="showReportDialog = false">取消</el-button>
        <el-button type="primary" @click="handleGenerateReport" :loading="generating">
          生成报告
        </el-button>
      </template>
    </el-dialog>

    <!-- 报告生成成功对话框 -->
    <el-dialog
      v-model="showSuccessDialog"
      title="报告生成成功"
      width="400px"
    >
      <el-result icon="success" title="报告已生成" :sub-title="`文件大小: ${formatFileSize(reportInfo?.file_size)}`">
        <template #extra>
          <el-button type="primary" @click="handleDownloadReport">
            <el-icon><Download /></el-icon>
            立即下载
          </el-button>
        </template>
      </el-result>
    </el-dialog>

    <!-- 部署命令对话框 -->
    <el-dialog
      v-model="showDeployDialog"
      title="部署命令"
      width="650px"
    >
      <p class="deploy-tip">在目标服务器上执行以下命令，即可自动部署巡检脚本并设置定时任务：</p>
      <pre class="deploy-command">{{ deployCommand }}</pre>
      <template #footer>
        <el-button @click="showDeployDialog = false">取消</el-button>
        <el-button type="primary" @click="copyDeployCommand">
          <el-icon><DocumentCopy /></el-icon>
          复制命令
        </el-button>
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
import { formatFileSize, downloadFile } from '@/utils/format'

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
      // 后端返回的数据结构: { project, statistics }
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
      
      // 获取每个主机的巡检次数
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
    console.error('获取主机巡检次数失败:', error)
    hostInspectionCounts.value[hostname] = 0
  }
}

// 获取主机巡检次数
const getHostInspectionCount = (hostname) => {
  return hostInspectionCounts.value[hostname] || 0
}

// 获取模板列表
const fetchTemplates = async () => {
  try {
    const res = await getTemplates()
    templates.value = res.data.templates || []
    
    // 自动选中推荐模板（默认为简化模板）
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
  const serverUrl = window.location.origin
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
    ElMessage.success('部署命令已复制到剪贴板')
    showDeployDialog.value = false
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
    downloadFile(response.data, filename)
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

.back-btn {
  margin-bottom: 20px;
}

.project-info-card {
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.card-header h2 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 8px;
}

.project-code {
  font-size: 14px;
  color: #909399;
}

.project-description {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 20px;
}

.project-statistics {
  display: flex;
  gap: 60px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.hosts-section {
  margin-top: 30px;
}

.hosts-section h3 {
  font-size: 20px;
  color: #303133;
  margin-bottom: 20px;
}

.hosts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.host-card {
  cursor: pointer;
  transition: all 0.3s;
}

.host-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.host-icon {
  text-align: center;
  margin-bottom: 15px;
}

.host-info h4 {
  font-size: 18px;
  color: #303133;
  margin-bottom: 6px;
}

.host-ip {
  font-size: 14px;
  color: #909399;
  margin-bottom: 12px;
}

.host-details {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.host-meta {
  display: flex;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #909399;
}

/* 已移除模板选择相关样式 */

.template-info-display {
  padding: 12px;
  background-color: #f0f9ff;
  border-left: 3px solid #409eff;
  border-radius: 4px;
  margin-top: 12px;
}

.template-info-display p {
  margin: 6px 0;
  font-size: 14px;
  color: #303133;
}

.template-desc-text {
  color: #606266 !important;
  font-size: 13px !important;
}

.loading-container {
  padding: 20px;
}

.deploy-tip {
  margin-bottom: 12px;
  color: #606266;
}

.deploy-command {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
