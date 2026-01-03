#!/bin/bash
# 简化版启动脚本 - 使用后台进程启动服务

set -e

echo "=========================================="
echo "  服务器巡检报告系统（简化版）"
echo "=========================================="

# 初始化数据库
echo "[1/3] 初始化数据库..."
cd /app && python3 -c "
import sys
sys.path.insert(0, '/app/backend')
from models.database import init_database
from services.template_service import TemplateService
init_database()
TemplateService.init_default_templates()
print('数据库和模板初始化完成！')
" || echo "初始化失败，但继续启动..."

# 创建数据目录
echo "[2/3] 创建数据目录..."
mkdir -p /app/data/screenshots /app/data/reports

# 启动后端服务（后台运行）
echo "[3/3] 启动后端服务..."
cd /app/backend
nohup python3 app.py > /var/log/backend.log 2>&1 &
BACKEND_PID=$!
echo "后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端启动
echo "等待后端服务就绪..."
for i in {1..30}; do
    if curl -s http://127.0.0.1:5000/health > /dev/null 2>&1; then
        echo "后端服务已就绪！"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "后端服务启动超时！"
        exit 1
    fi
    sleep 1
done

# 启动 Nginx（前台运行，保持容器运行）
echo "启动 Nginx..."
echo ""
echo "服务已启动："
echo "  - 前端: http://0.0.0.0:80"
echo "  - 后端: http://127.0.0.1:5000"
echo "  - 日志: /var/log/backend.log"
echo ""

# 定义信号处理函数
cleanup() {
    echo "正在关闭服务..."
    kill $BACKEND_PID 2>/dev/null || true
    nginx -s quit 2>/dev/null || true
    exit 0
}

trap cleanup SIGTERM SIGINT

# 启动 Nginx（前台运行）
exec nginx -g 'daemon off;'
