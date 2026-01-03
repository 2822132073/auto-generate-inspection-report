# Backend - 服务器巡检报告系统后端

基于 Flask 的 RESTful API 服务，提供巡检数据管理、报告生成和终端截图功能。

## 目录结构

```
backend/
├── api/                    # API 路由层
│   ├── inspection_routes.py   # 巡检记录 API
│   ├── project_routes.py      # 项目管理 API
│   ├── report_routes.py       # 报告生成 API
│   └── template_routes.py     # 模板管理 API
├── models/                 # 数据模型层
│   └── database.py            # SQLite 数据库模型
├── services/              # 业务逻辑层
│   ├── inspection_service.py  # 巡检业务逻辑
│   ├── project_service.py     # 项目业务逻辑
│   ├── report_service.py      # 报告生成逻辑
│   ├── screenshot_service.py  # 截图服务
│   └── template_service.py    # 模板管理
├── utils/                 # 工具函数
│   └── screenshot_generator.py # 终端截图生成器
├── app.py                 # Flask 应用入口
├── config.py              # 配置文件
└── requirements.txt       # Python 依赖
```

## 技术栈

- **框架**: Flask 2.3+
- **数据库**: SQLite3
- **文档生成**: python-docx
- **截图生成**: Playwright
- **跨域支持**: Flask-CORS

## 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

## 启动服务

### 方式一：直接运行
```bash
python app.py
```

### 方式二：指定端口
```bash
PORT=8000 python app.py
```

### 方式三：使用根目录启动脚本
```bash
cd ..
./start.sh
```

## API 文档

### 基础信息
- **Base URL**: `http://localhost:5000/api/v1`
- **默认端口**: 5000（可通过环境变量 PORT 修改）

### 主要端点

#### 1. 项目管理
- `GET /projects` - 获取项目列表
- `POST /projects` - 创建项目
- `GET /projects/{id}` - 获取项目详情
- `PUT /projects/{id}` - 更新项目
- `DELETE /projects/{id}` - 删除项目

#### 2. 巡检记录
- `GET /inspections` - 获取巡检记录列表
- `POST /inspections` - 提交巡检数据
- `GET /inspections/{id}` - 获取巡检详情
- `DELETE /inspections/{id}` - 删除巡检记录

#### 3. 报告生成
- `POST /reports/generate/{project_id}` - 生成巡检报告
- `GET /reports/download/{project_id}` - 下载报告
- `GET /projects/{project_id}/hosts` - 获取项目主机列表

#### 4. 截图访问
- `GET /screenshots/{path}` - 获取截图文件

#### 5. 系统信息
- `GET /stats` - 获取系统统计信息
- `GET /health` - 健康检查

## 数据目录

所有数据存储在 `../data/` 目录下：
- `data/inspections.db` - SQLite 数据库
- `data/screenshots/` - 终端截图文件
- `data/reports/` - 生成的报告文件

## 开发说明

### 添加新的 API 路由
1. 在 `api/` 目录创建路由文件
2. 在 `app.py` 中注册蓝图
3. 在 `services/` 中实现业务逻辑

### 数据库迁移
修改 `models/database.py` 中的表结构后，删除 `data/inspections.db` 重新初始化。

## 环境变量

- `PORT` - 服务端口（默认: 5000）
- `HOST` - 监听地址（默认: 0.0.0.0）

## 许可证

MIT License
