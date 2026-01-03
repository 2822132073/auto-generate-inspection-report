#!/bin/bash
# Backend 启动脚本

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  服务器巡检报告系统 - 后端服务${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 切换到 backend 目录
cd "$(dirname "$0")"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3，请先安装 Python 3.7+"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "../venv" ]; then
    echo -e "${GREEN}创建虚拟环境...${NC}"
    python3 -m venv ../venv
fi

# 激活虚拟环境
echo -e "${GREEN}激活虚拟环境...${NC}"
source ../venv/bin/activate

# 安装依赖
echo -e "${GREEN}检查依赖...${NC}"
pip install -q -r requirements.txt

# 设置默认端口
PORT=${PORT:-5000}

echo ""
echo -e "${GREEN}启动后端服务...${NC}"
echo -e "${BLUE}监听地址: http://0.0.0.0:${PORT}${NC}"
echo -e "${BLUE}API 文档: http://localhost:${PORT}/api/v1${NC}"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 启动服务
python app.py
