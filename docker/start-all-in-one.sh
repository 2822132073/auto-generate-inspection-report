#!/bin/bash
# 一体化容器快速启动脚本

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  服务器巡检报告系统 - 一体化容器部署"
echo "=========================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker 未安装"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: Docker Compose 未安装"
    echo "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info &> /dev/null; then
    echo "❌ 错误: Docker 服务未运行"
    echo "请先启动 Docker"
    exit 1
fi

echo "✅ Docker 环境检查通过"
echo ""

# 检查端口占用
if lsof -Pi :80 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  警告: 端口 80 已被占用"
    echo ""
    echo "占用进程:"
    lsof -i :80 || true
    echo ""
    read -p "是否修改为其他端口？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "请输入新端口号 (例如 8080): " NEW_PORT
        echo "正在修改 docker-compose.all-in-one.yml 中的端口..."
        sed -i.bak "s/\"80:80\"/\"$NEW_PORT:80\"/g" docker-compose.all-in-one.yml
        echo "✅ 端口已修改为 $NEW_PORT"
        PORT=$NEW_PORT
    else
        echo "❌ 取消部署"
        exit 1
    fi
else
    PORT=80
fi

echo ""
echo "📦 准备构建和启动容器..."
echo ""

# 选择部署方案
echo "请选择部署方案:"
echo "  1) Supervisord 方案（推荐，生产环境）"
echo "  2) 简化启动脚本方案（轻量级，开发测试）"
echo ""
read -p "请输入选项 (1/2, 默认 1): " DEPLOY_OPTION
DEPLOY_OPTION=${DEPLOY_OPTION:-1}

if [ "$DEPLOY_OPTION" = "2" ]; then
    echo "✅ 使用简化启动脚本方案"
    # 修改 docker-compose 文件使用简化版 Dockerfile
    if [ -f "docker-compose.all-in-one.yml" ]; then
        sed -i.bak 's/Dockerfile.all-in-one$/Dockerfile.all-in-one-simple/g' docker-compose.all-in-one.yml
    fi
else
    echo "✅ 使用 Supervisord 方案（推荐）"
    # 确保使用标准版 Dockerfile
    if [ -f "docker-compose.all-in-one.yml" ]; then
        sed -i.bak 's/Dockerfile.all-in-one-simple$/Dockerfile.all-in-one/g' docker-compose.all-in-one.yml
    fi
fi

echo ""
echo "🔨 开始构建镜像（首次构建可能需要 5-10 分钟）..."
docker-compose -f docker-compose.all-in-one.yml build

echo ""
echo "🚀 启动容器..."
docker-compose -f docker-compose.all-in-one.yml up -d

echo ""
echo "⏳ 等待服务启动..."
sleep 5

# 检查容器状态
if docker ps | grep -q "inspection-all-in-one"; then
    echo ""
    echo "=========================================="
    echo "  ✅ 部署成功！"
    echo "=========================================="
    echo ""
    echo "访问地址:"
    echo "  🌐 前端界面: http://localhost:$PORT"
    echo "  🔌 API 接口: http://localhost:$PORT/api/v1/"
    echo ""
    echo "管理命令:"
    echo "  查看日志: docker-compose -f docker-compose.all-in-one.yml logs -f"
    echo "  停止服务: docker-compose -f docker-compose.all-in-one.yml down"
    echo "  重启服务: docker-compose -f docker-compose.all-in-one.yml restart"
    echo "  进入容器: docker exec -it inspection-all-in-one bash"
    echo ""
    echo "或使用 Makefile 命令:"
    echo "  make all-in-one-logs    # 查看日志"
    echo "  make all-in-one-down    # 停止服务"
    echo "  make all-in-one-restart # 重启服务"
    echo "  make all-in-one-shell   # 进入容器"
    echo ""
    echo "数据目录:"
    echo "  ./data/screenshots/  # 截图存储"
    echo "  ./data/reports/      # 报告存储"
    echo "  ./data/inspection.db # 数据库"
    echo ""
    
    # 等待健康检查
    echo "⏳ 等待健康检查..."
    for i in {1..30}; do
        if docker exec inspection-all-in-one /app/healthcheck.sh &> /dev/null; then
            echo "✅ 所有服务健康检查通过！"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "⚠️  健康检查超时，但服务可能正在启动..."
            echo "   请稍后访问或查看日志: make all-in-one-logs"
        fi
        sleep 2
    done
    
    echo ""
    echo "🎉 部署完成，祝你使用愉快！"
else
    echo ""
    echo "❌ 容器启动失败，请查看日志:"
    echo "   docker-compose -f docker-compose.all-in-one.yml logs"
    exit 1
fi
