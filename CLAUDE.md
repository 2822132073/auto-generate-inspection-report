# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

接下来，请使用中文回复我，非必要不使用英文。

## Project Overview

一个基于 Python + Playwright + Vue.js 的服务器巡检报告生成系统，支持：
- **终端截图生成**：将命令执行记录转换为高质量终端截图
- **数据存储**：SQLite 数据库存储巡检记录
- **报告生成**：自动生成 DOCX 格式的项目巡检报告
- **异步截图**：后台任务队列处理截图生成（`screenshot_status: pending/processing/completed/failed/skipped`）
- **项目管理**：支持多项目、多主机的巡检管理
- **报告模板**：可配置的报告模板系统
- **HTTP API + Web UI**：完整的 RESTful API 和 Vue.js 前端

**核心特性**：支持多主机项目巡检，报告自动汇总每个主机的最新数据（按 timestamp 排序）。

## Common Commands

### 一键启动（推荐）

```bash
./start-all.sh    # 同时启动后端(8000)和前端(5173)
./stop-all.sh     # 停止所有服务
```

### 后端开发

```bash
# 进入后端目录
cd backend

# 激活虚拟环境
source ../venv/bin/activate

# 启动后端服务（自动初始化数据库和默认模板）
# 默认端口 8000（macOS 上 5000 端口被 AirPlay 占用）
PORT=8000 python app.py

# 安装依赖
pip install -r ../requirements.txt
playwright install chromium
```

**注意**：入口文件是 `backend/app.py`，而非项目根目录的 `api_server.py`（README 中的旧文档）。

### 前端开发

```bash
cd web-frontend
npm install       # 首次安装
npm run dev       # 启动开发服务器 (默认 5173)
```

### 数据库

数据库位于 `backend/data/inspections.db`，启动时自动初始化，无需手动操作。

## Architecture

### 项目结构

```
.
├── backend/                    # 后端代码
│   ├── app.py                  # Flask 应用入口（含后台截图线程）
│   ├── config.py               # 全局配置
│   ├── models/                 # 数据模型层
│   │   └── database.py         # SQLite 初始化和连接管理
│   ├── services/               # 业务服务层
│   │   ├── inspection_service.py
│   │   ├── screenshot_service.py
│   │   ├── screenshot_task_service.py  # 异步截图处理
│   │   ├── report_service.py
│   │   ├── project_service.py
│   │   └── template_service.py
│   ├── api/                    # API 路由层
│   │   ├── inspection_routes.py
│   │   ├── report_routes.py
│   │   ├── project_routes.py
│   │   └── template_routes.py
│   └── utils/                  # 工具层
│       ├── logger.py           # 统一日志配置
│       └── screenshot_generator.py  # Playwright 截图核心
│
├── web-frontend/               # Vue.js 前端
│   └── src/
│       ├── api/                # API 调用封装
│       ├── views/              # 页面组件
│       └── router/             # 路由配置
│
├── data/                       # 数据目录（自动创建）
│   ├── inspections.db          # SQLite 数据库
│   ├── screenshots/            # 截图存储（按 YYYY-MM/ 组织）
│   └── reports/                # 报告存储（按 YYYY-MM/ 组织）
│
├── venv/                       # Python 虚拟环境
├── start-all.sh                # 一键启动脚本
└── stop-all.sh                 # 停止服务脚本
```

### 分层架构

```
配置层 (config.py)
    ↓
数据模型层 (models/)
    ↓
业务服务层 (services/)
    ↓
API 路由层 (api/)
    ↓
HTTP 服务器 (app.py)
    ↓
前端 (web-frontend/)
```

### 代码模式

**后端 API 路由**：使用统一异常处理装饰器
```python
def handle_api_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"操作失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            logger.exception(f"操作异常: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    return wrapper

@inspection_bp.route('/inspections', methods=['POST'])
@handle_api_error
def create_inspection():
    # 无需 try-catch，由装饰器处理
    ...
```

**前端 API 调用**：使用 `createApi` 辅助函数
```javascript
// web-frontend/src/api/request.js
export function createApi(url, method = 'get') {
  return (data, config) => {
    const params = method === 'get' ? { params: data } : { data }
    return request({ url, method, ...params, ...config })
  }
}

// 使用示例
export const getInspections = createApi('/inspections')
export const createProject = createApi('/projects', 'post')
```

### 核心：异步截图处理

截图生成从同步改为异步，避免 API 请求超时：

1. **提交巡检** → 命令记录的 `screenshot_status` 设为 `pending` 或 `skipped`
2. **后台线程** (`ScreenshotTaskService.process_all_pending()`) 每 5 秒扫描待处理任务
3. **状态流转**：`pending` → `processing` → `completed/failed`

### 数据库表结构

| 表名 | 说明 |
|------|------|
| `inspection_records` | 巡检记录主表 |
| `command_executions` | 命令执行记录（含 `screenshot_status`） |
| `report_generations` | 报告生成记录 |
| `report_templates` | 报告模板配置 |
| `projects` | 项目管理表 |

### 关键业务逻辑

**多主机最新记录查询**：报告生成时，使用 SQL 子查询获取每个主机的最新数据：

```sql
SELECT ir.* FROM inspection_records ir
INNER JOIN (
    SELECT hostname, MAX(timestamp) as max_timestamp
    FROM inspection_records WHERE project_id = ?
    GROUP BY hostname
) latest ON ir.hostname = latest.hostname
    AND ir.timestamp = latest.max_timestamp
WHERE ir.project_id = ?
ORDER BY ir.hostname
```

**项目标识符解析** (`ProjectService.resolve_project_id()`)：支持通过项目ID、项目代码、项目名称三种方式查询项目。

**日志规范**：
- API 层：`api.{模块名}` (如 `api.inspection`)
- 服务层：`services.{服务名}`
- 工具层：`utils.{工具名}`
- 级别：`info`（操作成功）、`warning`（业务警告）、`error`（错误）、`exception`（异常+堆栈）、`debug`（调试）

## API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/api/v1/inspections` | 创建巡检记录 |
| `GET` | `/api/v1/inspections` | 查询列表（分页、筛选） |
| `GET` | `/api/v1/inspections/{id}` | 获取详情 |
| `DELETE` | `/api/v1/inspections/{id}` | 删除记录 |
| `GET` | `/api/v1/inspections/{id}/screenshot-status` | 查询截图生成状态 |
| `POST` | `/api/v1/inspections/{id}/regenerate-screenshots` | 重新生成截图 |
| `GET` | `/api/v1/projects` | 项目列表 |
| `POST` | `/api/v1/projects` | 创建项目 |
| `GET` | `/api/v1/projects/{id}/hosts` | 获取项目主机列表 |
| `POST` | `/api/v1/projects/{id}/report` | 生成项目报告 |
| `GET` | `/api/v1/projects/{id}/report` | 下载最新报告 |
| `GET` | `/api/v1/templates` | 模板列表 |
| `POST` | `/api/v1/templates` | 创建模板 |
| `GET` | `/health` | 健康检查 |
| `GET` | `/api/v1/stats` | 系统统计 |
| `GET` | `/api/v1/screenshots/{path}` | 访问截图文件 |

## Input JSON Format

```json
{
  "data": {
    "env": {
      "USER": "root",
      "PWD": "/root",
      "HOSTNAME": "node-1",
      "PS1": "\\[\\e]0;\\u@\\h: \\w\\a\\]${debian_chroot:+($debian_chroot)}\\u@\\h:\\w\\$ "
    },
    "commands": {
      "free -h": {
        "command": "free -h",
        "return_code": 0,
        "output": "..."
      }
    }
  },
  "metadata": {
    "project_id": "project-001",
    "ip": "192.168.1.10",
    "timestamp": "2026-01-08T10:00:00Z",
    "hostname": "node-1",
    "os": "Linux",
    "kernel": "5.15.0",
    "arch": "x86_64"
  },
  "options": {
    "generate_screenshots": true,  // true=异步生成, false=跳过
    "notes": "定期巡检"
  }
}
```

## Important Notes

1. **字体文件**：`OperatorMono-Medium.otf` 必须放在项目根目录
2. **文件存储**：截图和报告按月份组织（`YYYY-MM/`），数据库存相对路径
3. **级联删除**：删除巡检记录会自动删除关联的截图文件
4. **外键约束**：数据库启用 `PRAGMA foreign_keys = ON`
5. **中文支持**：JSON 用 `ensure_ascii=False`，DOCX 用 SimSun 字体

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `HOST` | 0.0.0.0 | 后端监听地址 |
| `PORT` | 8000 | 后端端口（macOS 上避免使用 5000，被 AirPlay 占用） |
| `BACKEND_PORT` | 8000 | start-all.sh 后端端口 |
| `FRONTEND_PORT` | 5173 | start-all.sh 前端端口 |
| `VITE_API_BASE_URL` | /api/v1 | 前端 API 基础路径 |
