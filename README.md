# 服务器巡检报告系统

基于 Python + Playwright 的服务器巡检报告生成系统，支持终端截图生成、数据存储和自动化报告生成。

## 功能特性

### 核心功能
- 🖼️ **终端截图生成** - 将命令执行记录转换为高质量终端截图
- 💾 **数据存储** - SQLite 数据库存储巡检记录
- 📊 **报告生成** - 自动生成 DOCX 格式的巡检报告
- 🌐 **HTTP API** - 完整的 RESTful API 接口

### 技术特性
- 🎨 支持自定义字体（默认使用 OperatorMono-Medium.otf）
- 📐 自动根据内容调整截图尺寸
- 🖥️ 高分辨率输出（支持 3x 设备像素比）
- 🔧 支持复杂的 PS1 提示符解析（包括 bash 条件表达式）
- 🏢 **多主机支持** - 按项目汇总多台主机的最新巡检信息
- 📝 **简洁报告** - 文本为主的 DOCX 报告，包含系统信息和截图

## 安装

### 1. 克隆项目

```bash
git clone <repository-url>
cd auto-generate-inspection-report
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. 初始化数据库

```bash
python init_db.py
```

## 使用方法

### 命令行工具

#### 基本用法

```bash
python generate_terminal_screenshot.py [json_file] [output_dir] [font_file]
```

参数说明：
- `json_file`: JSON 文件路径（默认: `test.json`）
- `output_dir`: 输出目录（默认: `output`）
- `font_file`: 字体文件名（默认: `OperatorMono-Medium.otf`）

#### 示例

```bash
# 使用默认参数
python generate_terminal_screenshot.py

# 指定输入文件和输出目录
python generate_terminal_screenshot.py test.json output

# 指定自定义字体
python generate_terminal_screenshot.py test.json output custom-font.otf
```

### HTTP API 服务（推荐）

#### 启动服务

服务启动时会自动初始化数据库。

```bash
python api_server.py
```

服务默认运行在 `http://0.0.0.0:5000`

可以通过环境变量配置：
- `PORT`: 端口号（默认: 5000）
- `HOST`: 主机地址（默认: 0.0.0.0）

```bash
PORT=8080 HOST=127.0.0.1 python api_server.py
```

#### API 端点

##### 巡检数据管理

**POST /api/v1/inspections** - 提交巡检数据

**请求体格式：**

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
  "metadata": {
    "project_id": "project-001",
    "ip": "172.19.0.4",
    "timestamp": "2026-01-01T13:52:02Z",
    "hostname": "node-1",
    "os": "Linux",
    "kernel": "5.15.0-139-generic",
    "arch": "x86_64"
  },
  "options": {
    "generate_screenshots": true,
    "notes": "定期巡检"
  }
}
```

**GET /api/v1/inspections** - 查询巡检记录（支持分页和筛选）

参数：`page`, `page_size`, `hostname`, `project_id`, `start_date`, `end_date`, `sort_by`, `sort_order`

**GET /api/v1/inspections/{id}** - 获取巡检记录详情

**DELETE /api/v1/inspections/{id}** - 删除巡检记录

##### 项目报告生成

**POST /api/v1/projects/{project_id}/report** - 生成项目巡检报告

自动获取该项目下所有主机的最新巡检记录，生成包含所有主机信息的 DOCX 报告。

**请求体格式：**

```json
{
  "options": {
    "title": "服务器巡检报告",
    "include_screenshots": true
  }
}
```

**GET /api/v1/projects/{project_id}/report** - 下载项目最新报告

**GET /api/v1/projects/{project_id}/hosts** - 获取项目下所有主机列表

##### 系统信息

**GET /api/v1/stats** - 系统统计信息

**GET /health** - 健康检查

##### 单个截图生成（保留原功能）

**POST /generate** - 生成单个终端截图

**请求体格式：**

```json
{
  "env": {
    "USER": "root",
    "PWD": "/root",
    "HOME": "/root",
    "HOSTNAME": "node-1",
    "PS1": "\\[\\e]0;\\u@\\h: \\w\\a\\]${debian_chroot:+($debian_chroot)}\\u@\\h:\\w\\$ "
  },
  "command": {
    "command": "free -h",
    "output": "total        used        free      shared  buff/cache   available\nMem:           15Gi       7.0Gi       417Mi       162Mi       7.9Gi       7.9Gi\nSwap:             0B          0B          0B",
    "return_code": 0
  },
  "font_file": "OperatorMono-Medium.otf",  // 可选，默认使用 OperatorMono-Medium.otf
  "scale_factor": 3  // 可选，默认 3
}
```

**参数说明：**

- `env` (必需): 环境变量字典，包含 `USER`, `PWD`, `HOSTNAME`, `PS1` 等
- `command` (必需): 命令对象，包含：
  - `command` (必需): 命令字符串
  - `output` (可选): 命令输出
  - `return_code` (可选): 返回码，默认 0
- `font_file` (可选): 字体文件名，默认 `OperatorMono-Medium.otf`
  - 如果指定的字体文件不存在，返回 400 错误
- `scale_factor` (可选): 设备像素比，默认 3（3x 分辨率）

**响应：**

- 成功: HTTP 200，Content-Type: `image/png`，返回 PNG 图片二进制数据
- 错误: HTTP 400/500，Content-Type: `application/json`，返回错误信息

**错误响应示例：**

```json
{
  "error": "字体文件不存在: custom-font.otf"
}
```

##### GET /health

健康检查端点

**响应：**

```json
{
  "status": "ok"
}
```

#### 典型使用流程

1. **提交巡检数据**（多台主机多次执行）

```bash
# 主机1第一次巡检
curl -X POST http://localhost:5000/api/v1/inspections \
  -H "Content-Type: application/json" \
  -d @test.json

# 修改主机名和IP，模拟主机2
curl -X POST http://localhost:5000/api/v1/inspections \
  -H "Content-Type: application/json" \
  -d @test2.json

# 主机1第二次巡检（更新的时间戳）
curl -X POST http://localhost:5000/api/v1/inspections \
  -H "Content-Type: application/json" \
  -d @test_updated.json
```

2. **查看项目主机列表**

```bash
curl http://localhost:5000/api/v1/projects/project-001/hosts
```

3. **生成项目报告**（包含所有主机的最新信息）

```bash
curl -X POST http://localhost:5000/api/v1/projects/project-001/report \
  -H "Content-Type: application/json" \
  -d '{"options": {"include_screenshots": true}}'
```

4. **下载报告**

```bash
curl http://localhost:5000/api/v1/projects/project-001/report \
  --output project_report.docx
```

#### 使用示例

##### 使用 curl（单个截图）

```bash
# 基本请求
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "env": {
      "USER": "root",
      "PWD": "/root",
      "HOSTNAME": "node-1",
      "PS1": "[\\u@\\h \\W]\\$ "
    },
    "command": {
      "command": "free -h",
      "output": "total        used        free\nMem:           15Gi       7.0Gi       417Mi",
      "return_code": 0
    }
  }' \
  --output screenshot.png

# 使用自定义字体（如果字体不存在会返回错误）
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "env": {...},
    "command": {...},
    "font_file": "custom-font.otf"
  }' \
  --output screenshot.png
```

##### 使用 Python

```python
import requests

url = "http://localhost:5000/generate"
data = {
    "env": {
        "USER": "root",
        "PWD": "/root",
        "HOSTNAME": "node-1",
        "PS1": "[\\u@\\h \\W]\\$ "
    },
    "command": {
        "command": "free -h",
        "output": "total        used        free\nMem:           15Gi       7.0Gi       417Mi",
        "return_code": 0
    }
}

response = requests.post(url, json=data)
if response.status_code == 200:
    with open('screenshot.png', 'wb') as f:
        f.write(response.content)
    print("截图已保存")
else:
    print(f"错误: {response.json()}")
```

## JSON 格式

输入 JSON 文件格式：

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
  "metadata": {
    "project_id": "unknown",
    "ip": "172.19.0.4",
    "timestamp": "2026-01-01T13:52:02Z",
    "hostname": "node-1"
  }
}
```

## 支持的 PS1 转义序列

- `\u` - 用户名
- `\h` - 主机名
- `\w` - 完整路径（支持 ~ 缩写）
- `\W` - 当前目录名
- `\$` - $ 或 #（根据用户是否为 root）
- `\e` - ESC 字符（会被移除）
- `\a` - 响铃字符（会被移除）
- `\[...\]` - 非打印字符序列（会被移除）

## 支持的 Bash 条件表达式

- `${var:+value}` - 如果变量存在则显示 value
- `${var:-value}` - 如果变量不存在则显示默认值 value

示例：`${debian_chroot:+($debian_chroot)}` - 如果 debian_chroot 存在，显示 `(debian_chroot的值)`

## 项目结构

```
auto-generate-inspection-report/
├── config.py                        # 全局配置
├── generate_terminal_screenshot.py  # 截图生成核心
├── api_server.py                    # HTTP API 服务器
├── init_db.py                       # 数据库初始化脚本
├── requirements.txt                 # Python 依赖
├── OperatorMono-Medium.otf          # 默认字体文件
├── test.json                        # 示例 JSON 文件
├── models/                          # 数据模型层
│   └── database.py                  # 数据库初始化和连接
├── services/                        # 业务服务层
│   ├── inspection_service.py        # 巡检数据处理
│   ├── screenshot_service.py        # 截图生成服务
│   └── report_service.py            # 报告生成服务
├── api/                             # API 路由层
│   ├── inspection_routes.py         # 巡检相关路由
│   └── report_routes.py             # 报告相关路由
├── data/                            # 数据目录
│   ├── inspections.db               # SQLite 数据库
│   ├── screenshots/                 # 截图存储（按月份）
│   └── reports/                     # 报告存储（按月份）
└── README.md                        # 项目文档
```

## DOCX 报告结构

项目报告按主机分章节组织：

```
服务器巡检报告 - 项目XXX
========================

项目信息：
  项目ID、报告生成时间、主机数量

一、主机1 (node-1)
  1.1 基本信息（表格）
      主机名、IP、操作系统、内核、架构、巡检时间

  1.2 系统信息汇总
      1.2.1 命令1
            返回码、执行结果、终端截图
      1.2.2 命令2
            ...

二、主机2 (node-2)
  2.1 基本信息
  2.2 系统信息汇总
      ...

三、主机3 (node-3)
  ...

页脚：报告生成时间
```

**重要特性**：
- 每个主机章节显示该主机**最新**的巡检信息（按 timestamp 排序）
- 支持多主机项目汇总
- 截图按月份组织存储，报告同样按月份组织

## 注意事项

1. 字体文件需要放在项目根目录下
2. 如果使用自定义字体，确保字体文件存在，否则 API 会返回错误
3. 截图分辨率由 `scale_factor` 控制，值越大分辨率越高，但文件也越大
4. 截图尺寸会根据内容自动调整，确保没有多余的空白
5. **数据库**：巡检数据存储在 `data/inspections.db`
6. **自动去重**：同一主机多次巡检，报告只包含最新数据

## 许可证

MIT License
