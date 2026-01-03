# 项目启动指南

## 当前运行状态

✅ **前端服务**: http://localhost:3000 (Vite 开发服务器)  
✅ **后端服务**: http://localhost:8000 (Flask API 服务器)

## 快速启动

### 方式一：使用启动脚本（推荐）

```bash
./start.sh
```

这个脚本会自动启动前后端服务。

### 方式二：手动启动

**1. 启动后端（终端1）**
```bash
PORT=8000 python api_server.py
```

**2. 启动前端（终端2）**
```bash
cd web-frontend
npm run dev
```

## 配置说明

前后端端口已分离：
- 前端运行在 **3000** 端口
- 后端运行在 **8000** 端口

环境变量配置文件：
- `web-frontend/.env.development` - 开发环境（指向 http://localhost:8000）
- `web-frontend/.env.production` - 生产环境（使用相对路径 /api/v1）

## 测试功能

1. 访问 http://localhost:3000
2. 查看项目列表页面
3. 点击项目进入详情页
4. 点击主机查看巡检记录
5. 在项目详情页点击"生成巡检报告"测试报告功能

## 停止服务

按 `Ctrl + C` 停止对应的服务进程。

## 注意事项

- 首次启动前端需要先运行 `cd web-frontend && npm install` 安装依赖
- 确保 Python 虚拟环境已激活
- 端口 3000 和 8000 不能被其他程序占用
