# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

接下来，请使用中文回复我，非必要不使用英文。

## Project Overview

一个基于 Python + Playwright 的服务器巡检报告生成系统，支持：
- 终端截图生成：将命令执行记录转换为高质量终端截图
- 数据存储：SQLite 数据库存储巡检记录
- 报告生成：自动生成 DOCX 格式的项目巡检报告
- HTTP API：完整的 RESTful API 接口

**核心特性**：支持多主机项目巡检，报告自动汇总每个主机的最新数据（按 timestamp 排序）。

## Development Setup

### Virtual Environment

The project uses a Python virtual environment located in `venv/`:

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
playwright install chromium
```

### Dependencies

- `playwright>=1.40.0` - Browser automation for rendering HTML to screenshots
- `flask>=2.3.0` - HTTP API server framework

## Common Commands

### 初始化和启动

```bash
# 初始化数据库（仅首次或手动重置时需要）
python init_db.py

# 启动 HTTP API 服务（会自动初始化数据库）
python api_server.py

# 使用环境变量配置
PORT=8080 HOST=127.0.0.1 python api_server.py
```

### 巡检数据管理

```bash
# 提交巡检数据
curl -X POST http://localhost:5000/api/v1/inspections \
  -H "Content-Type: application/json" \
  -d @test.json

# 查询巡检记录（分页）
curl "http://localhost:5000/api/v1/inspections?page=1&page_size=20"

# 按项目筛选
curl "http://localhost:5000/api/v1/inspections?project_id=project-001"

# 按主机筛选
curl "http://localhost:5000/api/v1/inspections?hostname=node-1"

# 获取详情
curl http://localhost:5000/api/v1/inspections/1

# 删除记录
curl -X DELETE http://localhost:5000/api/v1/inspections/1
```

### 项目报告生成

```bash
# 查看项目主机列表
curl http://localhost:5000/api/v1/projects/project-001/hosts

# 生成项目报告（汇总所有主机最新数据）
curl -X POST http://localhost:5000/api/v1/projects/project-001/report \
  -H "Content-Type: application/json" \
  -d '{"options": {"include_screenshots": true}}'

# 下载项目报告
curl http://localhost:5000/api/v1/projects/project-001/report \
  -o project_report.docx
```

### 系统信息

```bash
# 健康检查
curl http://localhost:5000/health

# 统计信息
curl http://localhost:5000/api/v1/stats
```

### 命令行工具（原有功能）

```bash
# Basic usage with defaults (reads test.json, outputs to output/)
python generate_terminal_screenshot.py

# Specify custom input file and output directory
python generate_terminal_screenshot.py <json_file> <output_dir>

# 使用自定义字体
python generate_terminal_screenshot.py test.json output CustomFont.otf
```

## Architecture

### 分层架构设计

```
配置层 (config.py)
    ↓
数据模型层 (models/)
    ↓
业务服务层 (services/)
    ↓
API 路由层 (api/)
    ↓
HTTP 服务器 (api_server.py)
```

### Core Components

**config.py** - 全局配置管理：
- 定义路径常量（DATA_DIR, SCREENSHOTS_DIR, REPORTS_DIR, DATABASE_PATH）
- API 配置（分页大小、版本）
- 报告配置（标题、截图宽度）
- 自动创建必要目录

**models/database.py** - 数据库层：
- `init_database()`: 创建表和索引（inspection_records, command_executions, report_generations）
- `get_db_connection()`: 上下文管理器，自动处理连接、事务、回滚

**services/screenshot_service.py** - 截图服务：
- `generate_and_save()`: 封装现有截图生成功能，保存到文件系统（按月份组织）

**services/inspection_service.py** - 巡检服务：
- `create_inspection()`: 保存巡检记录 + 命令 + 生成截图
- `get_inspections()`: 分页查询，支持多条件筛选
- `get_inspection_detail()`: 获取详情（包含所有命令）
- `delete_inspection()`: 删除记录和关联截图文件
- `get_project_latest_hosts()`: **核心方法** - 获取项目下每个主机的最新记录

**services/report_service.py** - 报告服务：
- `generate_project_report()`: 生成项目报告，按主机分章节
  - 调用 `get_project_latest_hosts()` 获取每个主机的最新数据
  - 使用 python-docx 生成 DOCX 文档
  - 支持中文字体（SimSun）
  - 嵌入截图和文本输出
- `_to_chinese_number()`: 数字转中文（一、二、三...）

**api/inspection_routes.py** - 巡检路由：
- `POST /api/v1/inspections`: 创建巡检记录
- `GET /api/v1/inspections`: 查询列表（分页、筛选）
- `GET /api/v1/inspections/<id>`: 获取详情
- `DELETE /api/v1/inspections/<id>`: 删除记录

**api/report_routes.py** - 报告路由：
- `GET /api/v1/projects/<project_id>/hosts`: 获取项目主机列表
- `POST /api/v1/projects/<project_id>/report`: 生成项目报告
- `GET /api/v1/projects/<project_id>/report`: 下载最新报告

**api_server.py** - Flask 应用：
- 注册蓝图（inspection_bp, report_bp）
- 启动时自动初始化数据库
- 提供系统统计端点（/api/v1/stats）
- 保留原有截图生成端点（/generate）

**generate_terminal_screenshot.py** - 截图生成核心（原有功能，保持不变）：
- `parse_ps1()`: Parses bash PS1 prompt templates, handling escape sequences (`\u`, `\h`, `\w`, `\W`, `\$`) and bash conditional expressions (`${var:+value}`, `${var:-value}`)
- `generate_single_command_html()`: Generates HTML representation of a terminal with prompt, command, and output
- `generate_screenshot_bytes()`: 渲染 HTML 到 PNG 使用 Playwright，返回字节流（API 使用）
- `generate_screenshot()`: 批量处理 JSON 文件，保存到文件（CLI 使用）
- `load_font_as_base64()`: 嵌入字体文件为 base64 data URI，确保一致渲染

### Data Flow

#### 巡检数据提交流程

```
客户端提交 JSON
    ↓
inspection_routes.create_inspection()
    ↓
InspectionService.create_inspection()
    ↓
1. 保存 inspection_records（主记录）
2. 遍历 commands，对每个命令：
   - ScreenshotService.generate_and_save()
     → generate_screenshot_bytes() 生成截图
     → 保存到 data/screenshots/YYYY-MM/
   - 保存 command_executions（命令记录）
    ↓
返回创建结果
```

#### 项目报告生成流程

```
请求生成项目报告
    ↓
report_routes.generate_project_report()
    ↓
ReportService.generate_project_report()
    ↓
1. InspectionService.get_project_latest_hosts(project_id)
   → SQL 查询：按 hostname 分组，选择每组 timestamp 最大的记录
   → 返回每个主机的最新巡检数据
2. 创建 DOCX 文档
   - 设置中文字体（SimSun + qn('w:eastAsia')）
   - 按主机分章节循环：
     a. 章节标题（一、二、三...）
     b. 基本信息表格
     c. 遍历命令，插入：
        - 返回码
        - 文本输出（Consolas 等宽字体）
        - 截图（从 SCREENSHOTS_DIR 加载）
3. 保存到 data/reports/YYYY-MM/
4. 记录到 report_generations 表
    ↓
返回报告信息（路径、大小、主机数）
```

### Key Design Decisions

**多主机最新记录查询**：使用 SQL 子查询实现，确保每个主机只显示最新数据：
```sql
SELECT ir.*
FROM inspection_records ir
INNER JOIN (
    SELECT hostname, MAX(timestamp) as max_timestamp
    FROM inspection_records
    WHERE project_id = ?
    GROUP BY hostname
) latest ON ir.hostname = latest.hostname
          AND ir.timestamp = latest.max_timestamp
WHERE ir.project_id = ?
ORDER BY ir.hostname
```

**文件存储策略**：
- 截图和报告按月份组织（YYYY-MM/），避免单目录文件过多
- 数据库存储相对路径，便于迁移
- 删除记录时级联删除文件

**事务管理**：`get_db_connection()` 上下文管理器自动处理：
- 成功时自动 commit
- 异常时自动 rollback
- 始终 close 连接

**中文支持**：
- JSON 存储使用 `ensure_ascii=False`
- DOCX 使用 SimSun 字体并设置 `qn('w:eastAsia')`
- 章节编号使用中文数字（一、二、三...）

## File Structure

```
.
├── config.py                        # 全局配置
├── generate_terminal_screenshot.py  # 截图生成核心
├── api_server.py                    # HTTP API 服务器
├── init_db.py                       # 数据库初始化脚本
├── requirements.txt                 # Python 依赖
├── OperatorMono-Medium.otf          # 默认字体文件
├── test.json                        # 示例 JSON 文件
├── models/                          # 数据模型层
│   ├── __init__.py
│   └── database.py                  # 数据库初始化和连接
├── services/                        # 业务服务层
│   ├── __init__.py
│   ├── inspection_service.py        # 巡检数据处理
│   ├── screenshot_service.py        # 截图生成服务
│   └── report_service.py            # 报告生成服务
├── api/                             # API 路由层
│   ├── __init__.py
│   ├── inspection_routes.py         # 巡检相关路由
│   └── report_routes.py             # 报告相关路由
├── data/                            # 数据目录（自动创建）
│   ├── inspections.db               # SQLite 数据库
│   ├── screenshots/                 # 截图存储（按月份）
│   └── reports/                     # 报告存储（按月份）
├── output/                          # CLI 输出目录（旧功能）
├── README.md                        # 项目文档
└── venv/                            # Python 虚拟环境
```

## Input JSON Format

```json
{
  "data": {
    "env": {
      "USER": "root",
      "PWD": "/root",
      "HOME": "/root",
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
  "metadata": { ... }
}
```

## API Request Format

```json
{
  "env": { "USER": "root", "PWD": "/root", "HOSTNAME": "node-1", "PS1": "..." },
  "command": { "command": "free -h", "output": "...", "return_code": 0 },
  "font_file": "OperatorMono-Medium.otf",  // Optional
  "scale_factor": 3  // Optional, default 3
}
```

## Important Notes

### 业务逻辑
- **多主机项目**：一个项目包含多台主机，每台主机可多次上传巡检数据
- **最新数据**：报告生成时，自动选择每个主机 timestamp 最新的记录
- **自动截图**：提交巡检数据时默认生成截图，可通过 `generate_screenshots: false` 禁用
- **按月归档**：截图和报告文件按月份组织（YYYY-MM/），便于管理

### 技术细节
- 字体文件必须放在项目根目录
- 默认字体 `OperatorMono-Medium.otf` 是必需的（除非指定其他字体）
- 截图分辨率由 `scale_factor` 控制（默认 3x，适合高清显示）
- API 启动时自动初始化数据库，无需手动运行 init_db.py
- 删除巡检记录时会级联删除关联的截图文件
- 数据库启用外键约束（PRAGMA foreign_keys = ON）

### 开发建议
- 修改数据库 schema：更新 models/database.py 中的 CREATE TABLE 语句
- 添加新 API 端点：在 api/ 目录创建新蓝图，在 api_server.py 注册
- 修改报告格式：编辑 services/report_service.py 中的 generate_project_report()
- 添加新的巡检字段：更新 inspection_records 表和相关服务层代码
