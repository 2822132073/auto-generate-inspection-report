#!/bin/bash
# 容器启动脚本 - 初始化环境并启动服务

set -e

echo "=========================================="
echo "  服务器巡检报告系统 - 一体化容器启动"
echo "=========================================="

# 初始化数据库
echo "[1/4] 初始化数据库..."
cd /app && python3 -c "
import sys
sys.path.insert(0, '/app/backend')
from models.database import init_database
from services.template_service import TemplateService

print('创建数据库表...')
init_database()
print('数据库初始化完成！')

print('初始化默认模板...')
TemplateService.init_default_templates()
print('模板初始化完成！')
" || {
    echo "数据库初始化失败，但继续启动..."
}

# 创建必要的目录并设置权限
echo "[2/4] 创建数据目录..."
mkdir -p /app/data/screenshots /app/data/reports
chmod -R 755 /app/data

# 测试 Nginx 配置
echo "[3/4] 检查 Nginx 配置..."
nginx -t || {
    echo "Nginx 配置错误！"
    exit 1
}

# 显示服务信息
echo "[4/4] 准备启动服务..."
echo ""
echo "服务配置："
echo "  - 后端 Flask API: http://127.0.0.1:5000"
echo "  - 前端 Vue.js:     http://0.0.0.0:80"
echo "  - API 代理路径:    /api/* -> http://127.0.0.1:5000"
echo "  - 数据目录:        /app/data"
echo ""
echo "启动进程管理器..."

# 执行传入的命令（supervisord）
exec "$@"
