<template>
  <div class="host-inspections">
    <!-- 返回按钮 -->
    <button class="back-btn" @click="goBack">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="15 18 9 12 15 6"/>
      </svg>
      <span>返回项目</span>
    </button>

    <!-- 主机信息卡片 -->
    <div class="host-info-card" v-if="hostInfo">
      <div class="host-banner">
        <div class="host-avatar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
            <line x1="8" y1="21" x2="16" y2="21"/>
            <line x1="12" y1="17" x2="12" y2="21"/>
          </svg>
        </div>
        <div class="host-details">
          <h1 class="host-name">{{ hostname }}</h1>
          <p class="host-ip">{{ hostInfo.ip }}</p>
        </div>
      </div>

      <div class="host-meta-grid">
        <div class="meta-item">
          <div class="meta-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
          </div>
          <div class="meta-content">
            <span class="meta-label">操作系统</span>
            <span class="meta-value">{{ hostInfo.os }}</span>
          </div>
        </div>
        <div class="meta-item">
          <div class="meta-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
          </div>
          <div class="meta-content">
            <span class="meta-label">内核版本</span>
            <span class="meta-value">{{ hostInfo.kernel }}</span>
          </div>
        </div>
        <div class="meta-item">
          <div class="meta-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="4" y="4" width="16" height="16" rx="2" ry="2"/>
              <rect x="9" y="9" width="6" height="6"/>
              <line x1="9" y1="1" x2="9" y2="4"/>
              <line x1="15" y1="1" x2="15" y2="4"/>
              <line x1="9" y1="20" x2="9" y2="23"/>
              <line x1="15" y1="20" x2="15" y2="23"/>
              <line x1="20" y1="9" x2="23" y2="9"/>
              <line x1="20" y1="14" x2="23" y2="14"/>
              <line x1="1" y1="9" x2="4" y2="9"/>
              <line x1="1" y1="14" x2="4" y2="14"/>
            </svg>
          </div>
          <div class="meta-content">
            <span class="meta-label">系统架构</span>
            <span class="meta-value">{{ hostInfo.arch }}</span>
          </div>
        </div>
        <div class="meta-item">
          <div class="meta-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <div class="meta-content">
            <span class="meta-label">项目归属</span>
            <span class="meta-value">{{ projectCode }}</span>
          </div>
        </div>
        <div class="meta-item">
          <div class="meta-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
          </div>
          <div class="meta-content">
            <span class="meta-label">巡检总次数</span>
            <span class="meta-value">{{ total }} 次</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 巡检记录时间线 -->
    <div class="timeline-section">
      <div class="section-header">
        <h2 class="section-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
          巡检记录
        </h2>
        <span class="section-count">共 {{ total }} 次</span>
      </div>

      <div v-if="loading" class="loading-container">
        <div v-for="i in 3" :key="i" class="skeleton-timeline-item">
          <div class="skeleton-dot"></div>
          <div class="skeleton-content">
            <div class="skeleton-title"></div>
            <div class="skeleton-text"></div>
          </div>
        </div>
      </div>

      <div v-else-if="inspections.length > 0" class="timeline-list">
        <div
          v-for="(inspection, index) in inspections"
          :key="inspection.id"
          class="timeline-item"
          :class="{ expanded: expandedIds.includes(inspection.id) }"
          :style="{ animationDelay: `${index * 0.05}s` }"
        >
          <!-- 时间线节点 -->
          <div class="timeline-node">
            <div class="timeline-dot" :class="inspection.status">
              <svg v-if="inspection.status === 'completed'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </div>
            <div class="timeline-date">{{ formatDateTime(inspection.timestamp) }}</div>
          </div>

          <!-- 记录卡片 -->
          <div class="record-card">
            <div class="record-header" @click="toggleInspection(inspection.id)">
              <div class="header-left">
                <div class="record-icon" :class="inspection.status">
                  <svg v-if="inspection.status === 'completed'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="8" x2="12" y2="12"/>
                    <line x1="12" y1="16" x2="12.01" y2="16"/>
                  </svg>
                </div>
                <div>
                  <h3 class="record-title">巡检记录 #{{ inspection.id }}</h3>
                  <span class="record-status" :class="inspection.status">
                    {{ inspection.status === 'completed' ? '已完成' : '失败' }}
                  </span>
                </div>
              </div>
              <div class="header-right">
                <span class="command-count">{{ inspection.commands_count }} 个命令</span>
                <button
                  class="regenerate-btn"
                  :class="{ loading: regeneratingIds.includes(inspection.id) }"
                  @click.stop="handleRegenerateScreenshots(inspection.id)"
                  :disabled="regeneratingIds.includes(inspection.id)"
                >
                  <svg v-if="!regeneratingIds.includes(inspection.id)" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="23 4 23 10 17 10"/>
                    <polyline points="1 20 1 14 7 14"/>
                    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
                  </svg>
                  <svg v-else class="spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
                  </svg>
                  <span>{{ regeneratingIds.includes(inspection.id) ? '生成中' : '重新生成' }}</span>
                </button>
                <button class="expand-btn" @click.stop="toggleInspection(inspection.id)">
                  <svg :class="{ rotated: expandedIds.includes(inspection.id) }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="6 9 12 15 18 9"/>
                  </svg>
                </button>
              </div>
            </div>

            <!-- 展开的详细信息 -->
            <el-collapse-transition>
              <div v-show="expandedIds.includes(inspection.id)" class="record-detail">
                <!-- 基本信息 -->
                <div class="detail-section">
                  <h4 class="detail-title">基本信息</h4>
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">记录 ID</span>
                      <span class="info-value">{{ inspection.id }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">巡检时间</span>
                      <span class="info-value">{{ formatDateTime(inspection.timestamp) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">状态</span>
                      <span class="info-value">
                        <span class="status-badge" :class="inspection.status">
                          {{ inspection.status }}
                        </span>
                      </span>
                    </div>
                    <div class="info-item" v-if="inspection.notes">
                      <span class="info-label">备注</span>
                      <span class="info-value">{{ inspection.notes }}</span>
                    </div>
                  </div>
                </div>

                <!-- 环境变量 -->
                <div class="detail-section" v-if="inspectionDetails[inspection.id]?.env">
                  <h4 class="detail-title">
                    环境变量
                    <button class="toggle-env-btn" @click="toggleEnv(inspection.id)">
                      {{ showEnv[inspection.id] ? '收起' : '展开' }}
                      <svg :class="{ rotated: showEnv[inspection.id] }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="6 9 12 15 18 9"/>
                      </svg>
                    </button>
                  </h4>
                  <el-collapse-transition>
                    <div v-show="showEnv[inspection.id]" class="env-table-wrapper">
                      <div class="env-table">
                        <div v-for="(value, key) in inspectionDetails[inspection.id].env" :key="key" class="env-row">
                          <span class="env-key">{{ key }}</span>
                          <span class="env-value">{{ value }}</span>
                        </div>
                      </div>
                    </div>
                  </el-collapse-transition>
                </div>

                <!-- 命令执行列表 -->
                <div class="detail-section" v-if="inspectionDetails[inspection.id]?.commands">
                  <h4 class="detail-title">命令执行列表</h4>
                  <div class="commands-list">
                    <div
                      v-for="(cmd, idx) in inspectionDetails[inspection.id].commands"
                      :key="idx"
                      class="command-item"
                    >
                      <div class="command-header">
                        <code class="command-text">{{ cmd.command }}</code>
                        <span class="command-status" :class="{ success: cmd.return_code === 0, error: cmd.return_code !== 0 }">
          返回码: {{ cmd.return_code }}
        </span>
                      </div>

                      <div class="command-output" v-if="cmd.output">
                        <div class="output-label">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="4 17 10 11 4 5"/>
                            <line x1="12" y1="19" x2="20" y2="19"/>
                          </svg>
                          执行结果
                        </div>
                        <pre class="output-content">{{ cmd.output }}</pre>
                      </div>

                      <div class="command-screenshot" v-if="cmd.screenshot_path">
                        <div class="output-label">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                            <circle cx="8.5" cy="8.5" r="1.5"/>
                            <polyline points="21 15 16 10 5 21"/>
                          </svg>
                          终端截图
                        </div>
                        <el-image
                          :src="getScreenshotUrl(cmd.screenshot_path)"
                          fit="contain"
                          :preview-src-list="[getScreenshotUrl(cmd.screenshot_path)]"
                          class="screenshot-img"
                        >
                          <template #error>
                            <div class="image-error">
                              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                                <circle cx="8.5" cy="8.5" r="1.5"/>
                                <polyline points="21 15 16 10 5 21"/>
                              </svg>
                              <span>截图加载失败</span>
                            </div>
                          </template>
                        </el-image>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </el-collapse-transition>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
        </div>
        <h3>该主机暂无巡检记录</h3>
        <p>请通过 API 提交巡检数据</p>
      </div>

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
import { ElMessage } from 'element-plus'
import { getInspections, getInspectionDetail, regenerateScreenshots } from '@/api/inspection'
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
const regeneratingIds = ref([])

// 重新生成截图
const handleRegenerateScreenshots = async (id) => {
  regeneratingIds.value.push(id)
  try {
    await regenerateScreenshots(id)
    ElMessage.success('已触发截图重新生成，请稍后刷新查看')
    delete inspectionDetails[id]
    await fetchInspectionDetail(id)
  } catch (error) {
    ElMessage.error('触发失败: ' + (error.message || '未知错误'))
  } finally {
    regeneratingIds.value = regeneratingIds.value.filter(i => i !== id)
  }
}

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

    if (inspections.value.length > 0 && !hostInfo.value) {
      hostInfo.value = inspections.value[0]
    }

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

// 获取截图 URL
const getScreenshotUrl = (path) => {
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

/* ===== 主机信息卡片 ===== */
.host-info-card {
  background: var(--bg-elevated);
  border-radius: 24px;
  padding: 32px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-md);
  margin-bottom: 32px;
}

.host-banner {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 28px;
}

.host-avatar {
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

.host-avatar svg {
  width: 40px;
  height: 40px;
}

.host-details .host-name {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.host-ip {
  font-size: 14px;
  color: var(--text-muted);
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
}

.host-meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border-radius: 14px;
  border: 1px solid var(--glass-border);
  transition: all 0.3s ease;
}

.meta-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.meta-icon {
  width: 40px;
  height: 40px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #667eea;
  flex-shrink: 0;
}

.meta-icon svg {
  width: 18px;
  height: 18px;
}

.meta-content {
  display: flex;
  flex-direction: column;
}

.meta-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 2px;
}

.meta-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

/* ===== 时间线区域 ===== */
.timeline-section {
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
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

.section-title svg {
  width: 22px;
  height: 22px;
  color: #667eea;
}

.section-count {
  padding: 8px 16px;
  background: var(--glass-bg);
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-muted);
}

/* ===== 加载状态 ===== */
.loading-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.skeleton-timeline-item {
  display: flex;
  gap: 20px;
  padding: 20px;
  background: var(--bg-elevated);
  border-radius: 16px;
  border: 1px solid var(--border-color);
}

.skeleton-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: linear-gradient(90deg, var(--bg-secondary) 25%, var(--bg-primary) 50%, var(--bg-secondary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  flex-shrink: 0;
  margin-top: 4px;
}

.skeleton-content {
  flex: 1;
}

.skeleton-title {
  height: 20px;
  border-radius: 6px;
  background: linear-gradient(90deg, var(--bg-secondary) 25%, var(--bg-primary) 50%, var(--bg-secondary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  margin-bottom: 10px;
}

.skeleton-text {
  height: 14px;
  border-radius: 6px;
  background: linear-gradient(90deg, var(--bg-secondary) 25%, var(--bg-primary) 50%, var(--bg-secondary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  width: 60%;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ===== 时间线列表 ===== */
.timeline-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.timeline-item {
  display: flex;
  gap: 24px;
  animation: fadeInUp 0.5s ease-out backwards;
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

.timeline-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.timeline-dot {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.timeline-dot.completed {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.timeline-dot:not(.completed) {
  background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
}

.timeline-dot svg {
  width: 20px;
  height: 20px;
}

.timeline-date {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-muted);
  text-align: center;
  white-space: nowrap;
}

/* ===== 记录卡片 ===== */
.record-card {
  flex: 1;
  background: var(--bg-elevated);
  border-radius: 20px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: all 0.3s ease;
}

.timeline-item.expanded .record-card {
  box-shadow: var(--shadow-md);
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.record-header:hover {
  background: var(--bg-primary);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.record-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.record-icon.completed {
  background: rgba(79, 172, 254, 0.1);
  color: #4facfe;
}

.record-icon:not(.completed) {
  background: rgba(245, 87, 108, 0.1);
  color: #f5576c;
}

.record-icon svg {
  width: 20px;
  height: 20px;
}

.record-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.record-status {
  font-size: 13px;
  padding: 4px 10px;
  border-radius: 6px;
  display: inline-block;
}

.record-status.completed {
  background: rgba(79, 172, 254, 0.15);
  color: #4facfe;
}

.record-status:not(.completed) {
  background: rgba(245, 87, 108, 0.15);
  color: #f5576c;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.command-count {
  padding: 6px 14px;
  background: var(--bg-primary);
  border-radius: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.regenerate-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--glass-bg);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.regenerate-btn svg {
  width: 14px;
  height: 14px;
}

.regenerate-btn:hover:not(:disabled) {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.regenerate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.regenerate-btn .spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.expand-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.expand-btn:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.expand-btn svg {
  width: 18px;
  height: 18px;
  transition: transform 0.3s ease;
}

.expand-btn svg.rotated {
  transform: rotate(180deg);
}

/* ===== 详情内容 ===== */
.record-detail {
  padding: 0 24px 24px;
  border-top: 1px solid var(--border-color);
}

.detail-section {
  padding: 20px 0;
}

.detail-section:not(:last-child) {
  border-bottom: 1px solid var(--border-color);
}

.detail-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.toggle-env-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-env-btn:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.toggle-env-btn svg {
  width: 14px;
  height: 14px;
  transition: transform 0.3s ease;
}

.toggle-env-btn svg.rotated {
  transform: rotate(180deg);
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-label {
  font-size: 12px;
  color: var(--text-muted);
}

.info-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.status-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.completed {
  background: rgba(79, 172, 254, 0.15);
  color: #4facfe;
}

.status-badge:not(.completed) {
  background: rgba(245, 87, 108, 0.15);
  color: #f5576c;
}

/* 环境变量表格 */
.env-table-wrapper {
  background: var(--bg-primary);
  border-radius: 12px;
  overflow: hidden;
}

.env-table {
  display: flex;
  flex-direction: column;
}

.env-row {
  display: flex;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.env-row:last-child {
  border-bottom: none;
}

.env-key {
  width: 200px;
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
  font-size: 13px;
  color: #667eea;
  font-weight: 500;
  flex-shrink: 0;
}

.env-value {
  flex: 1;
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
  font-size: 13px;
  color: var(--text-secondary);
  word-break: break-all;
}

/* 命令列表 */
.commands-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.command-item {
  background: var(--bg-primary);
  border-radius: 14px;
  padding: 16px;
}

.command-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.command-text {
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
  font-size: 13px;
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  padding: 8px 14px;
  border-radius: 8px;
}

.command-status {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.command-status.success {
  background: rgba(79, 172, 254, 0.15);
  color: #4facfe;
}

.command-status.error {
  background: rgba(245, 87, 108, 0.15);
  color: #f5576c;
}

.command-output {
  margin-top: 12px;
}

.output-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.output-label svg {
  width: 14px;
  height: 14px;
}

.output-content {
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
  font-size: 13px;
  background: var(--bg-secondary);
  padding: 14px;
  border-radius: 10px;
  overflow-x: auto;
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: var(--text-secondary);
}

.command-screenshot {
  margin-top: 12px;
}

.screenshot-img {
  max-width: 100%;
  width: auto;
  border-radius: 12px;
  cursor: pointer;
  border: 1px solid var(--border-color);
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 160px;
  background: var(--bg-primary);
  border-radius: 12px;
  color: var(--text-muted);
}

.image-error svg {
  width: 40px;
  height: 40px;
  margin-bottom: 8px;
}

/* ===== 空状态 ===== */
.empty-state {
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

.empty-state h3 {
  font-size: 18px;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-state p {
  color: var(--text-muted);
  font-size: 14px;
}

/* ===== 分页 ===== */
.pagination {
  margin-top: 32px;
  display: flex;
  justify-content: center;
}

:deep(.el-pagination) {
  --el-pagination-text-color: var(--text-secondary);
  --el-pagination-bg-color: var(--bg-elevated);
  --el-pagination-button-bg-color: var(--bg-primary);
  --el-pagination-button-color: var(--text-secondary);
  --el-pagination-hover-color: var(--text-primary);
}

:deep(.el-pagination.is-background .el-pager li) {
  background: var(--bg-primary);
  border-radius: 8px;
}

:deep(.el-pagination.is-background .el-pager li.is-active) {
  background: var(--primary-gradient);
  color: white;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .timeline-item {
    flex-direction: column;
    gap: 12px;
  }

  .timeline-node {
    flex-direction: row;
    width: 100%;
  }

  .timeline-date {
    margin-top: 0;
    margin-left: 12px;
  }

  .host-banner {
    flex-direction: column;
    text-align: center;
  }

  .host-meta-grid {
    grid-template-columns: 1fr;
  }

  .record-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-right {
    width: 100%;
    justify-content: space-between;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
