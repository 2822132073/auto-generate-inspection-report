# 服务器巡检报告系统

基于 Python + Playwright 的服务器巡检报告自动生成系统。支持多主机项目管理，自动生成终端截图和 DOCX 格式报告。

## 功能特性

- **终端截图生成** - 命令执行记录转换为高质量 PNG 截图
- **多主机支持** - 按项目管理多台服务器，自动汇总最新数据
- **自动报告** - 生成 DOCX 格式报告，按主机分章节组织
- **RESTful API** - 完整的增删查接口，支持分页和筛选
- **数据持久化** - SQLite 存储巡检记录，按月份归档文件

## 快速开始

### 环境要求

- Python 3.8+
- Chromium（Playwright 自动安装）

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd auto-generate-inspection-report

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
playwright install chromium
```

### 启动服务

```bash
python api_server.py
```

服务默认运行在 `http://0.0.0.0:5000`，启动时自动初始化数据库。

### 快速示例

```bash
# 1. 提交巡检数据
curl -X POST http://localhost:5000/api/v1/inspections \
  -H "Content-Type: application/json" \
  -d @test.json

# 2. 生成项目报告
curl -X POST http://localhost:5000/api/v1/projects/project-001/report

# 3. 下载报告
curl http://localhost:5000/api/v1/projects/project-001/report -o report.docx
```

## API 文档

### 巡检数据

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/v1/inspections` | 提交巡检数据 |
| GET | `/api/v1/inspections` | 查询列表（支持分页） |
| GET | `/api/v1/inspections/{id}` | 获取详情 |
| DELETE | `/api/v1/inspections/{id}` | 删除记录 |

查询参数：`page`, `page_size`, `hostname`, `project_id`, `start_date`, `end_date`

### 报告生成

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/v1/projects/{project_id}/hosts` | 获取项目主机列表 |
| POST | `/api/v1/projects/{project_id}/report` | 生成项目报告 |
| GET | `/api/v1/projects/{project_id}/report` | 下载最新报告 |

### 系统接口

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/api/v1/stats` | 系统统计 |
| POST | `/generate` | 生成单个截图 |

## 数据格式

### 提交巡检数据

```json
{
  "data": {
    "env": {
      "USER": "root",
      "PWD": "/root",
      "HOSTNAME": "node-1",
      "PS1": "[\\u@\\h \\W]\\$ "
    },
    "commands": {
      "free -h": {
        "command": "free -h",
        "return_code": 0,
        "output": "total   used   free\nMem:   15Gi   7.0Gi  417Mi"
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
    "generate_screenshots": true,
    "notes": "定期巡检"
  }
}
```

### 生成报告选项

```json
{
  "options": {
    "title": "服务器巡检报告",
    "include_screenshots": true
  }
}
```

## 命令行工具

除 API 外，也支持命令行直接生成截图：

```bash
python generate_terminal_screenshot.py [json_file] [output_dir] [font_file]
```

参数说明：
- `json_file` - JSON 文件路径（默认: test.json）
- `output_dir` - 输出目录（默认: output）
- `font_file` - 字体文件（默认: OperatorMono-Medium.otf）

## 配置说明

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `HOST` | 0.0.0.0 | 监听地址 |
| `PORT` | 5000 | 监听端口 |

### 目录结构

```
data/
├── inspections.db      # SQLite 数据库
├── screenshots/        # 截图存储（按月份）
│   └── 2026-01/
└── reports/            # 报告存储（按月份）
    └── 2026-01/
```

## 项目结构

```
├── api_server.py                    # HTTP 服务入口
├── generate_terminal_screenshot.py  # 截图生成核心
├── config.py                        # 全局配置
├── models/
│   └── database.py                  # 数据库层
├── services/
│   ├── inspection_service.py        # 巡检服务
│   ├── screenshot_service.py        # 截图服务
│   └── report_service.py            # 报告服务
├── api/
│   ├── inspection_routes.py         # 巡检路由
│   └── report_routes.py             # 报告路由
└── data/                            # 数据目录
```

## 报告结构

生成的 DOCX 报告按主机分章节：

```
服务器巡检报告 - 项目XXX
├── 项目信息（ID、时间、主机数）
├── 一、主机1 (node-1)
│   ├── 基本信息表格
│   └── 命令执行结果 + 截图
├── 二、主机2 (node-2)
│   └── ...
└── 页脚
```

每个主机章节显示该主机最新的巡检数据。

## 注意事项

1. 字体文件需放在项目根目录
2. 截图分辨率由 `scale_factor` 控制（默认 3x）
3. 同一主机多次巡检，报告只包含最新数据
4. 删除巡检记录会级联删除关联截图

## 许可证

MIT License
