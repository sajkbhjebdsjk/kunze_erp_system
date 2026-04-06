# Kunze ERP System - 快速部署指南

## 📋 部署前检查清单

- [ ] Python 3.8+ 已安装
- [ ] MySQL 8.0+ 已安装并运行
- [ ] 已创建数据库 `erp_system`
- [ ] 已复制 `.env.example` 为 `.env` 并修改配置
- [ ] 已安装依赖：`pip install -r requirements.txt`

## 🚀 快速开始

### 方式一：Windows 一键部署（推荐）

```bash
# 1. 安装依赖
deploy.bat install

# 2. 启动开发环境（用于测试）
deploy.bat dev

# 3. 启动生产服务器
deploy.bat start

# 4. 查看服务状态
deploy.bat status

# 5. 查看日志
deploy.bat logs
```

### 方式二：Linux/Mac Docker 部署

```bash
# 1. 配置环境变量
cp .env.example .env
vim .env  # 编辑配置

# 2. 启动服务（Web + MySQL）
./deploy.sh start

# 3. 生产环境部署（包含Nginx + SSL）
./deploy.sh production

# 4. 查看日志
./deploy.sh logs web

# 5. 备份数据库
./deploy.sh backup
```

### 方式三：传统部署

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
export $(cat .env | xargs)

# 3. 使用Gunicorn运行
cd backend
gunicorn --config ../gunicorn.conf.py app:app

# 或使用Flask开发服务器（仅限测试）
python app.py
```

## ⚙️ 环境配置说明

编辑 `.env` 文件：

```bash
# 数据库配置
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=你的密码        # 必须修改！
DB_NAME=erp_system

# JWT密钥（必须修改！）
JWT_SECRET_KEY=使用命令生成: python -c "import secrets; print(secrets.token_urlsafe(32))"

# CORS配置（生产环境必须设置）
CORS_ORIGINS=https://yourdomain.com

# 生产环境设置
FLASK_ENV=production       # 开发环境改为 development
FLASK_DEBUG=False          # 生产环境必须是 False
SESSION_COOKIE_SECURE=True # 生产环境必须是 True（需要HTTPS）
```

## 🔒 安全配置要点

### 必须修改的配置：
1. **DB_PASSWORD** - 数据库密码（不要使用默认值）
2. **JWT_SECRET_KEY** - JWT签名密钥（必须随机生成）
3. **SECRET_KEY** - Flask会话密钥（必须随机生成）
4. **CORS_ORIGINS** - 允许的域名白名单

### 生产环境安全检查：
```bash
# 启动时会自动检查安全配置
# 如果发现问题会显示警告或退出

# 手动检查（Python）:
python -c "from config.security import check_production_readiness; print(check_production_readiness())"
```

## 🐳 Docker 部署详细说明

### 基础部署（无Nginx）

```bash
# 构建镜像
docker build -t kunze-erp-system .

# 运行容器
docker run -d \
  --name kunze-erp \
  -p 5000:5000 \
  --env-file .env \
  -v ./uploads:/app/backend/uploads \
  -v ./logs:/app/backend/logs \
  kunze-erp-system
```

### 完整部署（Docker Compose）

```bash
# 启动所有服务（Web + MySQL）
docker-compose up -d --build

# 生产环境（Web + MySQL + Nginx + SSL）
docker-compose --profile production up -d --build

# 查看日志
docker-compose logs -f web

# 停止服务
docker-compose down

# 停止并删除数据卷（⚠️ 会丢失数据！）
docker-compose down -v
```

## 🌐 Nginx 配置（生产环境必需）

1. 获取SSL证书（推荐 Let's Encrypt）：
   ```bash
   certbot certonly --webroot -w /var/www/certbot -d yourdomain.com
   ```

2. 将证书放置到 `ssl/` 目录：
   ```
   ssl/fullchain.pem    # 完整证书链
   ssl/privkey.pem      # 私钥文件
   ```

3. 修改 `nginx.conf` 中的域名：
   ```nginx
   server_name yourdomain.com www.yourdomain.com;
   ```

4. 启动生产环境：
   ```bash
   ./deploy.sh production
   ```

## 📊 监控和维护

### 日志管理
- 应用日志：`backend/logs/system_YYYYMMDD.log`
- Nginx日志：`/var/log/nginx/access.log` 和 `error.log`
- Docker日志：`docker-compose logs -f`

### 性能监控
```bash
# 查看容器资源使用
docker stats

# 查看Gunicorn worker状态
curl http://localhost:5000/api/health
```

### 数据库备份
```bash
# 自动备份脚本已集成到 deploy.sh
./deploy.sh backup

# 备份文件位置：backups/YYYYMMDD_HHMMSS/backup.sql.gz
```

## ❓ 常见问题

### Q: 启动时提示 "JWT_SECRET_KEY 未设置"？
A: 请在 `.env` 文件中设置 `JWT_SECRET_KEY=你的随机密钥`

### Q: 访问页面显示跨域错误？
A: 在 `.env` 中配置 `CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:5000`

### Q: 上传文件失败？
A: 检查 `.env` 中的 `MAX_CONTENT_LENGTH_MB` 和目录权限

### Q: 如何查看当前运行模式？
A: 运行 `deploy.bat status` 或访问 `/api/health` 接口

## 📞 技术支持

如遇到问题，请检查：
1. 日志文件中的错误信息
2. 环境变量是否正确配置
3. 数据库连接是否正常
4. 端口是否被占用（默认5000）

---

**部署完成后访问地址：**
- 开发环境：http://localhost:5000
- 生产环境：https://yourdomain.com
