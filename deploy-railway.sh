#!/bin/bash
# =====================================================
# Kunze ERP System - Railway 快速部署助手 (Linux/Mac)
# 用法: ./deploy-railway.sh [命令]
# =====================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo -e "${CYAN}═════════════════════════════════════════${NC}"
echo -e "${CYAN}  🚄 Kunze ERP System - Railway 部署助手${NC}"
echo -e "${CYAN}═════════════════════════════════════════${NC}"
echo ""

# 显示帮助
show_help() {
    echo -e "${BLUE}用法: $0 {命令}${NC}"
    echo ""
    echo "命令:"
    echo "  prepare     准备部署（检查配置、生成密钥）"
    echo "  push        推送到 GitHub"
    echo "  check       检查 Railway 配置文件"
    echo "  env         显示环境变量模板"
    echo "  full        完整部署流程（prepare + push）"
    echo "  help        显示此帮助"
    echo ""
    echo "示例:"
    echo "  $0              # 显示菜单"
    echo "  $0 prepare      # 准备部署"
    echo "  $0 full         # 一键完成所有步骤"
}

# 准备部署
prepare_deploy() {
    echo -e "${YELLOW}[*] 步骤 1/4: 检查项目配置${NC}"
    echo ""
    
    MISSING_FILES=0
    
    # 检查必要文件
    for file in requirements.txt Procfile railway.json .gitignore; do
        if [ ! -f "$file" ]; then
            echo -e "${RED}[❌] 缺少 $file${NC}"
            ((MISSING_FILES++))
        else
            echo -e "${GREEN}[✓] $file 存在${NC}"
        fi
    done
    
    # 检查可选但推荐文件
    for file in runtime.txt nixpacks.toml gunicorn.conf.py; do
        if [ ! -f "$file" ]; then
            echo -e "${YELLOW}[⚠]  推荐: $file${NC}"
        else
            echo -e "${GREEN}[✓] $file 存在${NC}"
        fi
    done
    
    if [ "$MISSING_FILES" -gt 0 ]; then
        echo ""
        echo -e "${RED}[错误] 缺少 $MISSIVE_FILES 个必要文件！${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${YELLOW}[*] 步骤 2/4: 生成安全密钥${NC}"
    
    # 检查 Python 是否可用
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}[错误] Python3 未安装${NC}"
        exit 1
    fi
    
    # 生成 JWT 密钥
    JWT_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    echo -e "${GREEN}[✓] JWT_SECRET_KEY 已生成: ${JWT_KEY:0:20}...${NC}"
    
    # 生成 Flask 密钥
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    echo -e "${GREEN}[✓] SECRET_KEY 已生成: ${SECRET_KEY:0:20}...${NC}"
    
    echo ""
    echo -e "${YELLOW}[*] 步骤 3/4: 创建 Railway 环境变量文件${NC}"
    
    cat > railway-env-generated.txt << EOF
# Railway 环境变量 - 自动生成于 $(date '+%Y-%m-%d %H:%M:%S')
# 复制这些值到 Railway Dashboard → Variables

# ==================== 数据库配置 ====================
# 如果使用 Railway MySQL 插件，使用以下引用:
DB_HOST=\${{MySQL.HOST}}
DB_PORT=\${{MySQL.PORT}}
DB_USER=\${{MySQL.USER}}
DB_PASSWORD=\${{MySQL.PASSWORD}}
DB_NAME=\${{MySQL.DATABASE}}
DB_CHARSET=utf8mb4

# ==================== 安全配置（已自动生成）====================
JWT_SECRET_KEY=$JWT_KEY
SECRET_KEY=$SECRET_KEY
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# ==================== Flask 配置 ====================
FLASK_ENV=production
FLASK_DEBUG=False

# ==================== CORS 配置 ====================
# 部署后替换为你的实际 URL:
CORS_ORIGINS=https://your-app-name.up.railway.app

# ==================== 会话安全 ====================
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# ==================== 服务器配置 ====================
HOST=0.0.0.0
PORT=\${{PORT}}
WORKERS=2
LOG_LEVEL=info
EOF
    
    echo -e "${GREEN}[✓] 环境变量已保存到 railway-env-generated.txt${NC}"
    
    echo ""
    echo -e "${YELLOW}[*] 步骤 4/4: 更新 .gitignore${NC}"
    
    # 确保 .gitignore 包含必要条目
    for pattern in ".env" "railway-env-generated.txt" "__pycache__/" "*.log"; do
        if ! grep -q "^${pattern}$" .gitignore 2>/dev/null; then
            echo "$pattern" >> .gitignore
            echo -e "${GREEN}[✓] 已添加 ${pattern} 到 .gitignore${NC}"
        fi
    done
    
    echo ""
    echo -e "${GREEN}═════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✅ 部署准备工作完成！${NC}"
    echo -e "${GREEN}═════════════════════════════════════════${NC}"
    echo ""
    echo "下一步:"
    echo "  1. 运行 ./deploy-railway.sh push 推送到 GitHub"
    echo "  2. 登录 https://railway.app"
    echo "  3. 新建项目 → Deploy from GitHub repo"
    echo "  4. 在 Variables 中粘贴 railway-env-generated.txt 的内容"
    echo "  5. 添加 MySQL 服务（可选但推荐）"
    echo "  6. 点击 Deploy Now"
    echo ""
}

# 推送到 GitHub
push_to_github() {
    echo -e "${YELLOW}[*] 推送到 GitHub...${NC}"
    echo ""
    
    # 检查 Git 是否初始化
    if [ ! -d ".git" ]; then
        echo "正在初始化 Git 仓库..."
        git init
        git add .
        git commit -m "Initial commit: Kunze ERP System with Railway config"
        
        echo ""
        echo "请输入你的 GitHub 仓库地址:"
        echo "示例: https://github.com/username/kunze_erp_system.git"
        echo ""
        read -p "GitHub 仓库地址: " REPO_URL
        
        if [ -z "$REPO_URL" ]; then
            echo -e "${RED}[错误] 仓库地址不能为空${NC}"
            exit 1
        fi
        
        git remote add origin "$REPO_URL"
    else
        git add .
        git commit -m "Update: Prepare for Railway deployment" || true
    fi
    
    echo ""
    echo "正在推送到 GitHub..."
    
    if git push -u origin main 2>&1; then
        echo ""
        echo -e "${GREEN}[✅] 成功推送到 GitHub！${NC}"
        echo ""
        echo "现在可以登录 Railway 进行部署了:"
        echo "  https://railway.app/new → Deploy from GitHub repo"
    else
        echo ""
        echo -e "${RED}[❌] 推送失败！可能的原因:${NC}"
        echo "  1. 仓库地址不正确"
        echo "  2. 认证信息过期（请配置 SSH key 或 GitHub CLI）"
        echo "  3. 网络问题"
    fi
}

# 检查配置
check_config() {
    echo -e "${YELLOW}[*] 检查 Railway 部署配置文件...${NC}"
    echo ""
    
    CONFIG_OK=0
    
    echo "=== 必需文件检查 ==="
    for file in Procfile railway.json runtime.txt nixpacks.toml gunicorn.conf.py; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}[✓] $file${NC}"
            ((CONFIG_OK++))
        else
            echo -e "${RED}[❌] $file 缺失${NC}"
        fi
    done
    
    echo ""
    echo "=== 检查结果: $CONFIG_OK/5 个文件就绪 ==="
    
    if [ "$CONFIG_OK" -eq 5 ]; then
        echo -e "${GREEN}[✅] 所有配置文件齐全，可以部署到 Railway！${NC}"
    else
        echo -e "${YELLOW}[⚠️]  缺少部分配置文件，建议先运行 prepare 命令${NC}"
    fi
}

# 显示环境变量模板
show_env_template() {
    echo -e "${CYAN}═════════════════════════════════════════${NC}"
    echo -e "${CYAN}  Railway 环境变量模板${NC}"
    echo -e "${CYAN}═════════════════════════════════════════${NC}"
    echo ""
    echo "复制以下内容到 Railway Dashboard → Variables:"
    echo ""
    echo "────────────────────────────────────────"
    cat railway.env.example
    echo "────────────────────────────────────────"
    echo ""
    echo "提示:"
    echo "  - 使用 \${{} } 引用 Railway MySQL 变量"
    echo "  - 必须修改 JWT_SECRET_KEY 和 SECRET_KEY"
    echo "  - PORT 变量不要修改（Railway 动态分配）"
}

# 完整部署流程
full_deploy() {
    prepare_deploy
    push_to_github
}

# 主程序
case "${1:-}" in
    prepare)
        prepare_deploy
        ;;
    push)
        push_to_github
        ;;
    check)
        check_config
        ;;
    env)
        show_env_template
        ;;
    full)
        full_deploy
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        echo ""
        echo "请选择操作:"
        echo ""
        echo "  [1] 准备部署（检查配置并生成密钥）"
        echo "  [2] 推送到 GitHub"
        echo "  [3] 检查 Railway 配置文件"
        echo "  [4] 显示环境变量模板"
        echo "  [5] 完整部署流程（1+2）"
        echo "  [0] 退出"
        echo ""
        read -p "请输入选项 (0-5): " choice
        
        case "$choice" in
            1) prepare_deploy ;;
            2) push_to_github ;;
            3) check_config ;;
            4) show_env_template ;;
            5) full_deploy ;;
            0|q|Q) exit 0 ;;
            *) 
                echo "无效选项"
                exit 1
                ;;
        esac
        ;;
    *)
        echo -e "${RED}未知命令: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
