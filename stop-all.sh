#!/bin/bash
# 停止所有服务

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}停止服务器巡检报告系统...${NC}"
echo ""

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

# 停止后端
if [ -f "${PROJECT_ROOT}/.backend.pid" ]; then
    BACKEND_PID=$(cat "${PROJECT_ROOT}/.backend.pid")
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${GREEN}停止后端服务 (PID: ${BACKEND_PID})...${NC}"
        kill $BACKEND_PID
        rm "${PROJECT_ROOT}/.backend.pid"
    else
        echo -e "${YELLOW}后端服务未运行${NC}"
        rm "${PROJECT_ROOT}/.backend.pid"
    fi
else
    echo -e "${YELLOW}未找到后端 PID 文件${NC}"
fi

# 停止前端
if [ -f "${PROJECT_ROOT}/.frontend.pid" ]; then
    FRONTEND_PID=$(cat "${PROJECT_ROOT}/.frontend.pid")
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${GREEN}停止前端服务 (PID: ${FRONTEND_PID})...${NC}"
        kill $FRONTEND_PID
        rm "${PROJECT_ROOT}/.frontend.pid"
    else
        echo -e "${YELLOW}前端服务未运行${NC}"
        rm "${PROJECT_ROOT}/.frontend.pid"
    fi
else
    echo -e "${YELLOW}未找到前端 PID 文件${NC}"
fi

# 强制杀死可能残留的进程
BACKEND_PORT=${BACKEND_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-5173}

echo ""
echo -e "${GREEN}清理端口占用...${NC}"

# 清理后端端口
BACKEND_PIDS=$(lsof -ti:$BACKEND_PORT 2>/dev/null)
if [ -n "$BACKEND_PIDS" ]; then
    echo -e "${YELLOW}清理后端端口 ${BACKEND_PORT}...${NC}"
    echo $BACKEND_PIDS | xargs kill -9 2>/dev/null
fi

# 清理前端端口
FRONTEND_PIDS=$(lsof -ti:$FRONTEND_PORT 2>/dev/null)
if [ -n "$FRONTEND_PIDS" ]; then
    echo -e "${YELLOW}清理前端端口 ${FRONTEND_PORT}...${NC}"
    echo $FRONTEND_PIDS | xargs kill -9 2>/dev/null
fi

echo ""
echo -e "${GREEN}✓ 所有服务已停止${NC}"
