#!/bin/bash
# 启动脚本 - 同时启动前后端服务

echo "🚀 正在启动服务器巡检报告系统..."
echo ""

# 检查是否在项目根目录
if [ ! -f "api_server.py" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 启动后端服务
echo "📡 启动后端 API 服务器 (端口 8000)..."
PORT=8000 python api_server.py &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
echo ""

# 等待后端启动
sleep 2

# 启动前端服务
echo "🎨 启动前端开发服务器 (端口 3000)..."
cd web-frontend
npm run dev &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 服务启动成功！"
echo ""
echo "📍 前端地址: http://localhost:3000"
echo "📍 后端地址: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 等待用户中断
wait
