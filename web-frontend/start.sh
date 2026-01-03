#!/bin/bash
# Frontend 启动脚本

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  服务器巡检报告系统 - 前端服务${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 切换到 web-frontend 目录
cd "$(dirname "$0")"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}错误: 未找到 node，请先安装 Node.js${NC}"
    exit 1
fi

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}错误: 未找到 npm，请先安装 npm${NC}"
    exit 1
fi

# 设置默认端口
PORT=${PORT:-5173}

# 检查端口是否被占用
check_and_kill_port() {
    local port=$1
    echo -e "${GREEN}检查端口 ${port} 是否被占用...${NC}"
    
    # 查找占用端口的进程
    local pid=$(lsof -ti:${port})
    
    if [ -n "$pid" ]; then
        echo -e "${YELLOW}端口 ${port} 被进程 ${pid} 占用${NC}"
        echo -e "${YELLOW}正在终止进程...${NC}"
        kill -9 $pid 2>/dev/null
        sleep 1
        echo -e "${GREEN}进程已终止${NC}"
    else
        echo -e "${GREEN}端口 ${port} 可用${NC}"
    fi
}

# 检查并杀死占用的端口
check_and_kill_port $PORT

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo -e "${GREEN}安装依赖...${NC}"
    npm install
else
    echo -e "${GREEN}依赖已安装${NC}"
fi

echo ""
echo -e "${GREEN}启动前端开发服务器...${NC}"
echo -e "${BLUE}访问地址: http://localhost:${PORT}${NC}"
echo -e "${BLUE}API 地址: http://localhost:5000/api/v1${NC}"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 启动服务
npm run dev
