# 服务器巡检报告系统 - Web 前端

基于 Vue 3 + Element Plus 构建的服务器巡检报告系统前端界面。

## 技术栈

- **框架**: Vue 3
- **UI 组件库**: Element Plus
- **路由**: Vue Router
- **HTTP 客户端**: Axios
- **日期处理**: Day.js
- **构建工具**: Vite

## 功能特性

### 三层导航结构
- ✅ 项目列表页 - 展示所有项目
- ✅ 项目详情页 - 展示主机列表和生成报告
- ✅ 主机巡检记录页 - 时间线展示历史记录

### 核心功能
- 📊 项目和主机统计信息展示
- 🖥️ 主机卡片式展示
- ⏱️ 巡检记录时间线
- 📝 报告模板选择
- 📥 一键生成和下载报告
- 🖼️ 终端截图预览

## 快速开始

### 1. 安装依赖

```bash
cd web-frontend
npm install
```

### 2. 配置说明

前端和后端运行在不同端口：
- **前端开发服务器**: http://localhost:3000
- **后端 API 服务器**: http://localhost:8000

环境变量已配置在 `.env.development` 文件中，默认指向 `http://localhost:8000`

### 3. 启动后端服务

在项目根目录启动后端 API 服务器：

```bash
cd ..
PORT=8000 python api_server.py
```

### 4. 启动前端开发服务器

```bash
npm run dev
```

访问: http://localhost:3000

### 生产构建

```bash
npm run build
```

构建产物在 `dist` 目录。

### 预览构建

```bash
npm run preview
```

## 目录结构

```
web-frontend/
├── src/
│   ├── api/                 # API 接口封装
│   │   ├── request.js       # Axios 配置
│   │   ├── project.js       # 项目接口
│   │   ├── inspection.js    # 巡检接口
│   │   └── report.js        # 报告接口
│   ├── views/               # 页面组件
│   │   ├── ProjectList.vue      # 项目列表
│   │   ├── ProjectDetail.vue    # 项目详情
│   │   └── HostInspections.vue  # 主机巡检记录
│   ├── router/              # 路由配置
│   │   └── index.js
│   ├── utils/               # 工具函数
│   │   ├── date.js          # 日期格式化
│   │   └── format.js        # 数据格式化
│   ├── App.vue              # 根组件
│   └── main.js              # 入口文件
├── public/                  # 静态资源
├── index.html               # HTML 模板
├── vite.config.js           # Vite 配置
└── package.json             # 依赖配置
```

## 环境变量

项目已配置环境文件：

**开发环境** (`.env.development`)：
```bash
VITE_API_BASE_URL=http://localhost:8000
```

**生产环境** (`.env.production`)：
```bash
VITE_API_BASE_URL=/api/v1
```

生产环境下，前后端部署在同一域名，通过 Nginx 代理 `/api` 路径到后端服务。

## 路由说明

| 路径 | 页面 | 说明 |
|------|------|------|
| `/` | 项目列表 | 首页,展示所有项目 |
| `/projects/:projectCode` | 项目详情 | 展示项目信息和主机列表 |
| `/projects/:projectCode/hosts/:hostname` | 主机巡检记录 | 展示主机的巡检历史 |

## API 接口

前端调用后端 API，开发环境默认连接到 `http://localhost:8000`：

- `GET /api/v1/stats` - 系统统计
- `GET /api/v1/projects` - 项目列表
- `GET /api/v1/projects/{id}/hosts` - 项目主机
- `GET /api/v1/inspections` - 巡检记录
- `GET /api/v1/templates` - 报告模板
- `POST /api/v1/projects/{id}/report` - 生成报告
- `GET /api/v1/projects/{id}/report` - 下载报告

## 部署

### 方案一:与后端同服务器

1. 构建前端:
```bash
npm run build
```

2. 将 `dist` 目录复制到后端项目

3. 配置 Flask 静态文件路由

### 方案二:独立 Nginx 服务器(推荐)

1. 构建前端:
```bash
npm run build
```

2. 配置 Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /path/to/dist;
    index index.html;
    
    # 前端路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # 启用 Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}
```

## 开发说明

### 代码规范

- 组件名使用 PascalCase
- 方法名使用 camelCase
- 使用 Composition API (setup)
- 适当添加注释

### 样式规范

- 使用 scoped 样式
- 颜色使用 Element Plus 变量
- 响应式断点: 768px, 1200px, 1920px

## 浏览器支持

- Chrome (推荐)
- Firefox
- Safari
- Edge

不支持 IE 浏览器。

## 常见问题

### API 请求失败

确保后端服务在端口 8000 运行：
```bash
PORT=8000 python api_server.py
```

检查环境变量配置：`.env.development` 文件中的 `VITE_API_BASE_URL`

### 端口冲突

修改 `vite.config.js` 中的端口配置。

## License

MIT
