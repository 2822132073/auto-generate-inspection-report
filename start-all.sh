#!/bin/bash
# 一键启动脚本 - 同时启动前后端服务

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  服务器巡检报告系统 - 一键启动        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

# 后端端口
BACKEND_PORT=${BACKEND_PORT:-8000}
# 前端端口
FRONTEND_PORT=${FRONTEND_PORT:-5173}

# 检查并杀死占用端口的进程
check_and_kill_port() {
    local port=$1
    local service=$2
    
    echo -e "${GREEN}[${service}] 检查端口 ${port}...${NC}"
    
    # 查找占用端口的进程
    local pid=$(lsof -ti:${port} 2>/dev/null)
    
    if [ -n "$pid" ]; then
        echo -e "${YELLOW}[${service}] 端口 ${port} 被进程 ${pid} 占用，正在终止...${NC}"
        kill -9 $pid 2>/dev/null
        sleep 1
        echo -e "${GREEN}[${service}] 进程已终止${NC}"
    else
        echo -e "${GREEN}[${service}] 端口 ${port} 可用${NC}"
    fi
}

# 检查端口占用
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  检查端口占用${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
check_and_kill_port $BACKEND_PORT "后端"
check_and_kill_port $FRONTEND_PORT "前端"
echo ""

# 启动后端服务
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  启动后端服务${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
cd "${PROJECT_ROOT}/backend"

# 检查虚拟环境
if [ ! -d "${PROJECT_ROOT}/venv" ]; then
    echo -e "${GREEN}创建虚拟环境...${NC}"
    python3 -m venv "${PROJECT_ROOT}/venv"
fi

# 激活虚拟环境
source "${PROJECT_ROOT}/venv/bin/activate"

# 安装后端依赖
echo -e "${GREEN}检查后端依赖...${NC}"
pip install -q -r requirements.txt

# 后台启动后端
echo -e "${GREEN}启动后端服务 (端口: ${BACKEND_PORT})...${NC}"
PORT=$BACKEND_PORT nohup python app.py > "${PROJECT_ROOT}/backend.log" 2>&1 &

# 等待 PID 文件生成
echo -e "${GREEN}等待后端服务启动...${NC}"
for i in {1..10}; do
    if [ -f "${PROJECT_ROOT}/.backend.pid" ]; then
        break
    fi
    sleep 0.5
done

# 从 PID 文件读取真实的 Python 进程 PID
if [ -f "${PROJECT_ROOT}/.backend.pid" ]; then
    BACKEND_PID=$(cat "${PROJECT_ROOT}/.backend.pid")
    echo -e "${GREEN}后端服务 PID: ${BACKEND_PID}${NC}"
    
    # 验证进程是否真的在运行
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${GREEN}✓ 后端服务启动成功 (PID: ${BACKEND_PID})${NC}"
    else
        echo -e "${RED}✗ 后端服务启动失败，进程不存在，请查看 backend.log${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ 后端服务启动失败，未找到 PID 文件，请查看 backend.log${NC}"
    exit 1
fi
echo ""

# 启动前端服务
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  启动前端服务${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
cd "${PROJECT_ROOT}/web-frontend"

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo -e "${GREEN}安装前端依赖...${NC}"
    npm install
else
    echo -e "${GREEN}前端依赖已安装${NC}"
fi

# 后台启动前端
echo -e "${GREEN}启动前端服务 (端口: ${FRONTEND_PORT})...${NC}"
nohup npm run dev > "${PROJECT_ROOT}/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "${PROJECT_ROOT}/.frontend.pid"
sleep 3

# 检查前端是否启动成功
if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${GREEN}✓ 前端服务启动成功 (PID: ${FRONTEND_PID})${NC}"
else
    echo -e "${RED}✗ 前端服务启动失败，请查看 frontend.log${NC}"
    exit 1
fi
echo ""

# 显示服务信息
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  服务启动成功！                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📡 后端 API:${NC}    http://localhost:${BACKEND_PORT}/api/v1"
echo -e "${GREEN}🌐 前端界面:${NC}    http://localhost:${FRONTEND_PORT}"
echo ""
echo -e "${YELLOW}📝 日志文件:${NC}"
echo -e "   后端: ${PROJECT_ROOT}/backend.log"
echo -e "   前端: ${PROJECT_ROOT}/frontend.log"
echo ""
echo -e "${YELLOW}🛑 停止服务:${NC}"
echo -e "   运行: ${PROJECT_ROOT}/stop-all.sh"
echo -e "   或手动: kill ${BACKEND_PID} ${FRONTEND_PID}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 跟踪前端日志
echo -e "${GREEN}正在跟踪前端日志 (Ctrl+C 不会停止服务)...${NC}"
echo ""
tail -f "${PROJECT_ROOT}/frontend.log"
