#!/bin/bash
# =====================================================
# Kunze ERP System - 快速部署脚本
# 用法: ./deploy.sh [start|stop|restart|status|logs]
# =====================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Kunze ERP System - 部署管理脚本${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查依赖
check_dependencies() {
    echo -e "\n${YELLOW}检查依赖...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker 未安装${NC}"
        echo "   请安装 Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose 未安装${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ 依赖检查通过${NC}"
}

# 检查环境配置
check_env() {
    echo -e "\n${YELLOW}检查环境配置...${NC}"
    
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  .env 文件不存在，从 .env.example 复制...${NC}"
        cp .env.example .env
        echo -e "${RED}❗ 请编辑 .env 文件配置生产环境参数！${NC}"
        exit 1
    fi
    
    # 检查关键配置
    source .env
    
    if [ "$FLASK_ENV" = "production" ] && [ -z "$JWT_SECRET_KEY" ]; then
        echo -e "${RED}❌ 生产环境必须设置 JWT_SECRET_KEY${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ 环境配置检查通过${NC}"
}

# 启动服务
start_services() {
    echo -e "\n${YELLOW}启动服务...${NC}"
    
    check_dependencies
    check_env
    
    # 创建必要目录
    mkdir -p uploads logs ssl
    
    # 构建并启动（不包含nginx）
    docker-compose up -d --build web db
    
    echo -e "\n${GREEN}✓ 服务已启动${NC}"
    echo -e "  Web: http://localhost:5000"
    echo -e "  MySQL: localhost:3306"
    
    show_status
}

# 停止服务
stop_services() {
    echo -e "\n${YELLOW}停止服务...${NC}"
    docker-compose down
    echo -e "${GREEN}✓ 服务已停止${NC}"
}

# 重启服务
restart_services() {
    echo -e "\n${YELLOW}重启服务...${NC}"
    stop_services
    sleep 2
    start_services
}

# 显示状态
show_status() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}  服务状态${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    
    docker-compose ps
    
    echo -e "\n${BLUE}容器资源使用:${NC}"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# 查看日志
show_logs() {
    local service=${1:-}
    
    if [ -z "$service" ]; then
        echo -e "${YELLOW}查看所有服务日志 (Ctrl+C 退出)...${NC}"
        docker-compose logs -f --tail=100
    else
        echo -e "${YELLOW}查看 $service 日志 (Ctrl+C 退出)...${NC}"
        docker-compose logs -f --tail=100 "$service"
    fi
}

# 生产环境部署（包含Nginx）
deploy_production() {
    echo -e "\n${YELLOW}生产环境部署模式${NC}"
    echo -e "${RED}⚠️  此模式将启动 Nginx 反向代理${NC}"
    echo -e "${RED}   请确保已配置 SSL 证书${NC}"
    
    read -p "是否继续？(y/N) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "取消操作"
        return
    fi
    
    check_dependencies
    check_env
    
    # 创建SSL证书目录
    mkdir -p ssl
    
    # 检查SSL证书
    if [ ! -f "ssl/fullchain.pem" ] || [ ! -f "ssl/privkey.pem" ]; then
        echo -e "${YELLOW}⚠️  SSL证书未找到${NC}"
        echo "   请将证书文件放置到 ssl/ 目录："
        echo "     - fullchain.pem (完整证书链)"
        echo "     - privkey.pem (私钥)"
        echo ""
        echo "   或使用 Let's Encrypt 免费证书："
        echo "   https://letsencrypt.org/getting-started/"
        
        read -p "是否继续不使用SSL？（仅用于测试）(y/N) " -n 1 -r
        echo
        
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
    fi
    
    # 启动所有服务（包括Nginx）
    docker-compose --profile production up -d --build
    
    echo -e "\n${GREEN}✓ 生产环境部署完成${NC}"
    echo -e "  HTTPS: https://yourdomain.com"
    echo -e "  HTTP:  http://yourdomain.com (将重定向到HTTPS)"
}

# 数据库备份
backup_database() {
    echo -e "\n${YELLOW}备份数据库...${NC}"
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    source .env
    
    docker exec kunze-erp-db mysqldump \
        -u root \
        -p"${DB_PASSWORD}" \
        --single-transaction \
        --routines \
        --triggers \
        "${DB_NAME:-erp_system}" > "$BACKUP_DIR/backup.sql"
    
    gzip "$BACKUP_DIR/backup.sql"
    
    echo -e "${GREEN}✓ 数据库备份完成: ${BACKUP_DIR}/backup.sql.gz${NC}"
}

# 清理资源
cleanup() {
    echo -e "\n${YELLOW}清理Docker资源...${NC}"
    
    echo "停止的容器:"
    docker system prune -f
    
    echo "未使用的镜像:"
    docker image prune -a -f
    
    echo -e "${GREEN}✓ 清理完成${NC}"
}

# 主菜单
case "${1:-}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "${2:-}"
        ;;
    production)
        deploy_production
        ;;
    backup)
        backup_database
        ;;
    cleanup)
        cleanup
        ;;
    *)
        echo -e "\n${BLUE}用法: $0 {命令}${NC}"
        echo ""
        echo "命令:"
        echo "  start       启动开发环境服务（Web + MySQL）"
        echo "  stop        停止所有服务"
        echo "  restart     重启服务"
        echo "  status      查看服务状态和资源使用"
        echo "  logs        查看日志 [service_name]"
        echo "  production  生产环境部署（包含Nginx + SSL）"
        echo "  backup      备份数据库"
        echo "  cleanup     清理Docker资源"
        echo ""
        echo "示例:"
        echo "  $0 start              # 启动服务"
        echo "  $0 logs web           # 查看Web服务日志"
        echo "  $0 production         # 生产环境部署"
        echo "  $0 backup             # 备份数据库"
        ;;
esac
