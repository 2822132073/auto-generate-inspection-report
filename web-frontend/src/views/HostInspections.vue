<template>
  <div class="host-inspections">
    <!-- 返回按钮 -->
    <el-button @click="goBack" class="back-btn">
      <el-icon><ArrowLeft /></el-icon>
      返回
    </el-button>

    <!-- 主机信息卡片 -->
    <el-card class="host-info-card" v-if="hostInfo">
      <template #header>
        <div class="card-header">
          <div>
            <h2>{{ hostname }}</h2>
            <p class="host-ip">{{ hostInfo.ip }}</p>
          </div>
        </div>
      </template>

      <div class="host-details-grid">
        <div class="detail-item">
          <span class="label">操作系统:</span>
          <span class="value">{{ hostInfo.os }}</span>
        </div>
        <div class="detail-item">
          <span class="label">内核版本:</span>
          <span class="value">{{ hostInfo.kernel }}</span>
        </div>
        <div class="detail-item">
          <span class="label">系统架构:</span>
          <span class="value">{{ hostInfo.arch }}</span>
        </div>
        <div class="detail-item">
          <span class="label">项目归属:</span>
          <span class="value">{{ projectCode }}</span>
        </div>
        <div class="detail-item">
          <span class="label">巡检总次数:</span>
          <span class="value">{{ total }} 次</span>
        </div>
      </div>
    </el-card>

    <!-- 巡检记录时间线 -->
    <div class="timeline-section">
      <h3>巡检记录 (共 {{ total }} 次)</h3>

      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>

      <el-timeline v-else-if="inspections.length > 0" class="inspection-timeline">
        <el-timeline-item
          v-for="(inspection, index) in inspections"
          :key="inspection.id"
          :timestamp="formatDateTime(inspection.timestamp)"
          placement="top"
          :type="inspection.status === 'completed' ? 'success' : 'danger'"
        >
          <el-card class="timeline-card">
            <div class="timeline-header" @click="toggleInspection(inspection.id)">
              <div class="header-left">
                <el-icon v-if="inspection.status === 'completed'" color="#67c23a"><CircleCheck /></el-icon>
                <el-icon v-else color="#f56c6c"><CircleClose /></el-icon>
                <span class="record-title">巡检记录 #{{ inspection.id }}</span>
              </div>
              <div class="header-right">
                <el-tag size="small">{{ inspection.commands_count }} 个命令</el-tag>
                <el-button
                  :icon="expandedIds.includes(inspection.id) ? 'ArrowUp' : 'ArrowDown'"
                  size="small"
                  text
                >
                  {{ expandedIds.includes(inspection.id) ? '收起' : '展开' }}
                </el-button>
              </div>
            </div>

            <!-- 展开的详细信息 -->
            <el-collapse-transition>
              <div v-show="expandedIds.includes(inspection.id)" class="timeline-detail">
                <!-- 基本信息 -->
                <div class="detail-section">
                  <h4>基本信息</h4>
                  <el-descriptions :column="2" border size="small">
                    <el-descriptions-item label="记录 ID">{{ inspection.id }}</el-descriptions-item>
                    <el-descriptions-item label="巡检时间">{{ formatDateTime(inspection.timestamp) }}</el-descriptions-item>
                    <el-descriptions-item label="状态">
                      <el-tag :type="inspection.status === 'completed' ? 'success' : 'danger'" size="small">
                        {{ inspection.status }}
                      </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="备注" v-if="inspection.notes">
                      {{ inspection.notes }}
                    </el-descriptions-item>
                  </el-descriptions>
                </div>

                <!-- 环境变量 -->
                <div class="detail-section" v-if="inspectionDetails[inspection.id]?.env">
                  <h4>
                    环境变量
                    <el-button @click="toggleEnv(inspection.id)" size="small" text>
                      {{ showEnv[inspection.id] ? '收起' : '展开' }}
                    </el-button>
                  </h4>
                  <el-collapse-transition>
                    <el-table
                      v-show="showEnv[inspection.id]"
                      :data="formatEnvData(inspectionDetails[inspection.id].env)"
                      size="small"
                      border
                      max-height="300"
                    >
                      <el-table-column prop="key" label="变量名" width="200" />
                      <el-table-column prop="value" label="变量值" />
                    </el-table>
                  </el-collapse-transition>
                </div>

                <!-- 命令执行列表 -->
                <div class="detail-section" v-if="inspectionDetails[inspection.id]?.commands">
                  <h4>命令执行列表</h4>
                  <div class="commands-list">
                    <el-card
                      v-for="(cmd, idx) in inspectionDetails[inspection.id].commands"
                      :key="idx"
                      class="command-card"
                      shadow="never"
                    >
                      <div class="command-header">
                        <code class="command-text">{{ cmd.command }}</code>
                        <el-tag
                          :type="cmd.return_code === 0 ? 'success' : 'danger'"
                          size="small"
                        >
                          返回码: {{ cmd.return_code }}
                        </el-tag>
                      </div>

                      <div class="command-output" v-if="cmd.output">
                        <div class="output-label">执行结果:</div>
                        <pre class="output-content">{{ cmd.output }}</pre>
                      </div>

                      <div class="command-screenshot" v-if="cmd.screenshot_path">
                        <div class="output-label">终端截图:</div>
                        <el-image
                          :src="getScreenshotUrl(cmd.screenshot_path)"
                          fit="contain"
                          :preview-src-list="[getScreenshotUrl(cmd.screenshot_path)]"
                          class="screenshot-img"
                        >
                          <template #error>
                            <div class="image-error">
                              <el-icon><Picture /></el-icon>
                              <span>加载失败</span>
                            </div>
                          </template>
                        </el-image>
                      </div>
                    </el-card>
                  </div>
                </div>
              </div>
            </el-collapse-transition>
          </el-card>
        </el-timeline-item>
      </el-timeline>

      <el-empty
        v-else
        description="该主机暂无巡检记录"
        :image-size="150"
      />

      <!-- 分页 -->
      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="fetchInspections"
        @size-change="fetchInspections"
        class="pagination"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getInspections, getInspectionDetail } from '@/api/inspection'
import { formatDateTime } from '@/utils/date'

const router = useRouter()
const route = useRoute()
const projectCode = route.params.projectCode
const hostname = route.params.hostname

const loading = ref(false)
const inspections = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const hostInfo = ref(null)
const expandedIds = ref([])
const inspectionDetails = reactive({})
const showEnv = reactive({})

// 获取巡检记录列表
const fetchInspections = async () => {
  loading.value = true
  try {
    const res = await getInspections({
      hostname: hostname,
      project_id: projectCode,
      page: page.value,
      page_size: pageSize.value,
      sort_by: 'timestamp',
      sort_order: 'desc'
    })
    
    inspections.value = res.data.records || []
    total.value = res.data.total || 0
    
    // 设置主机信息(从第一条记录获取)
    if (inspections.value.length > 0 && !hostInfo.value) {
      hostInfo.value = inspections.value[0]
    }
    
    // 默认展开第一条记录
    if (inspections.value.length > 0 && expandedIds.value.length === 0) {
      const firstId = inspections.value[0].id
      expandedIds.value.push(firstId)
      await fetchInspectionDetail(firstId)
    }
  } catch (error) {
    console.error('获取巡检记录失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取巡检记录详情
const fetchInspectionDetail = async (id) => {
  if (inspectionDetails[id]) return
  
  try {
    const res = await getInspectionDetail(id)
    inspectionDetails[id] = res.data
  } catch (error) {
    console.error('获取巡检详情失败:', error)
  }
}

// 切换展开/收起
const toggleInspection = async (id) => {
  const index = expandedIds.value.indexOf(id)
  if (index > -1) {
    expandedIds.value.splice(index, 1)
  } else {
    expandedIds.value.push(id)
    await fetchInspectionDetail(id)
  }
}

// 切换环境变量显示
const toggleEnv = (id) => {
  showEnv[id] = !showEnv[id]
}

// 格式化环境变量数据
const formatEnvData = (env) => {
  if (!env) return []
  return Object.entries(env).map(([key, value]) => ({ key, value }))
}

// 获取截图 URL
const getScreenshotUrl = (path) => {
  // 使用环境变量构建完整 URL
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
  return `${baseURL}/screenshots/${path}`
}

// 返回上一页
const goBack = () => {
  router.push(`/projects/${projectCode}`)
}

onMounted(() => {
  fetchInspections()
})
</script>

<style scoped>
.host-inspections {
  max-width: 1200px;
  margin: 0 auto;
}

.back-btn {
  margin-bottom: 20px;
}

.host-info-card {
  margin-bottom: 30px;
}

.card-header h2 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 6px;
}

.host-ip {
  font-size: 14px;
  color: #909399;
}

.host-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.detail-item {
  display: flex;
  gap: 8px;
}

.detail-item .label {
  color: #909399;
  font-size: 14px;
}

.detail-item .value {
  color: #303133;
  font-size: 14px;
  font-weight: 500;
}

.timeline-section h3 {
  font-size: 20px;
  color: #303133;
  margin-bottom: 20px;
}

.inspection-timeline {
  margin-top: 20px;
}

.timeline-card {
  margin-bottom: 0;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.record-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.timeline-detail {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  font-size: 16px;
  color: #303133;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.commands-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.command-card {
  background: #fafafa;
}

.command-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.command-text {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  color: #409eff;
  background: #ecf5ff;
  padding: 4px 8px;
  border-radius: 4px;
}

.command-output {
  margin-top: 12px;
}

.output-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.output-content {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  line-height: 1.5;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.command-screenshot {
  margin-top: 12px;
}

.screenshot-img {
  max-width: 800px;
  width: 100%;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  cursor: pointer;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  background: #f5f7fa;
  color: #909399;
}

.pagination {
  margin-top: 24px;
  justify-content: center;
}

.loading-container {
  padding: 20px;
}
</style>
