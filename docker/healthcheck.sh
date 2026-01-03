#!/bin/bash
# 健康检查脚本 - 确保前端和后端服务都正常运行

set -e

# 检查后端健康状态
backend_health=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/health || echo "000")

if [ "$backend_health" != "200" ]; then
    echo "Backend health check failed: HTTP $backend_health"
    exit 1
fi

# 检查前端（Nginx）健康状态
frontend_health=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:80/ || echo "000")

if [ "$frontend_health" != "200" ]; then
    echo "Frontend health check failed: HTTP $frontend_health"
    exit 1
fi

# 检查 Nginx 进程
if ! pgrep nginx > /dev/null; then
    echo "Nginx process not running"
    exit 1
fi

# 检查 Python 进程
if ! pgrep -f "python.*app.py" > /dev/null; then
    echo "Backend process not running"
    exit 1
fi

echo "All services healthy"
exit 0
