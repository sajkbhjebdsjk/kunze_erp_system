# 🚄 Railway 平台部署指南

## 📋 目录
- [快速开始（5分钟部署）](#-快速开始5分钟部署)
- [详细步骤](#-详细步骤)
- [环境变量配置](#-环境变量配置)
- [数据库配置（MySQL）](#-数据库配置mysql)
- [常见问题解决](#-常见问题解决)
- [高级配置](#-高级配置)

---

## ⚡ 快速开始（5分钟部署）

### 前置条件
✅ GitHub 账号  
✅ Railway 账号（免费注册：https://railway.app）  
✅ 项目代码已推送到 GitHub  

### 一键部署步骤

```bash
# 1. 将项目推送到 GitHub（如果还没有）
git init
git add .
git commit -m "准备 Railway 部署"
git remote add origin https://github.com/你的用户名/kunze_erp_system.git
git push -u origin main

# 2. 登录 Railway 并部署
#    访问: https://railway.app/new
#    选择 "Deploy from GitHub repo"
#    选择你的仓库 → 点击 "Deploy Now"

# 3. 等待构建完成（约2-3分钟）
#    Railway 会自动检测 Python 项目并安装依赖
```

**完成！** 🎉 你的应用将在 `https://你的应用名.up.railway.app` 上线。

---

## 📖 详细步骤

### 第1步：准备 GitHub 仓库

#### 1.1 创建 .gitignore（已完成 ✅）
确保项目根目录有 `.gitignore` 文件，已排除：
- `.env` （敏感信息）
- `__pycache__/`
- `*.log`
- `uploads/`

#### 1.2 推送代码到 GitHub

```bash
# 初始化 Git（如果还没有）
cd c:\Users\26320\Desktop\kunze_erp_system

# 添加所有文件
git add .

# 创建首次提交
git commit -m "feat: 项目初始化，添加 Railway 部署配置"

# 连接远程仓库（替换为你的 GitHub 地址）
git remote add origin https://github.com/YOUR_USERNAME/kunze_erp_system.git

# 推送到 GitHub
git push -u origin main
```

> 💡 **提示**: 如果推送时提示 `.env` 文件被忽略，这是正常的！`.env` 已在 `.gitignore` 中。

---

### 第2步：在 Railway 创建项目

#### 2.1 登录 Railway
1. 访问 https://railway.app
2. 使用 GitHub 账号登录（推荐）
3. 点击 **"New Project"** 或 **"+"** 按钮

#### 2.2 选择部署方式
选择 **"Deploy from GitHub repo"**

#### 2.3 授权并选择仓库
1. 点击 **"Configure GitHub App"**
2. 授权 Railway 访问你的 GitHub
3. 在仓库列表中选择 `kunze_erp_system`
4. 点击 **"Deploy Now"**

Railway 会自动：
- 🔍 检测到 Python 项目（通过 `requirements.txt`）
- 📦 安装所有依赖
- 🔧 根据 `Procfile` 或 `railway.json` 启动应用
- 🌐 分配公网 URL

---

### 第3步：添加 MySQL 数据库

Railway 提供免费的 MySQL 数据库插件！

#### 3.1 添加 MySQL 服务
1. 在 Railway Dashboard 中，点击 **"+"** 按钮
2. 选择 **"Database"** → **"MySQL"**
3. 等待创建完成（约30秒）

#### 3.2 获取数据库连接信息
创建完成后，点击 MySQL 服务卡片，你会看到：

```
Host: xxx.railway.app
Port: 3306 (或 Railway 动态端口)
User: root
Password: 自动生成的密码
Database: railway (或自定义名称)
```

#### 3.3 配置环境变量（关键！）
在 Dashboard 中点击 **"Variables"** 标签页，添加以下环境变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `DB_HOST` | `${{MySQL.HOST}}` | Railway 自动填充 |
| `DB_PORT` | `${{MySQL.PORT}}` | Railway 自动填充 |
| `DB_USER` | `${{MySQL.USER}}` | Railway 自动填充 |
| `DB_PASSWORD` | `${{MySQL.PASSWORD}}` | Railway 自动填充 |
| `DB_NAME` | `${{MySQL.DATABASE}}` | Railway 自动填充 |

> 💡 **技巧**: Railway 支持 `${{ServiceName.VARIABLE}}` 语法自动引用其他服务的变量！

---

### 第4步：配置应用环境变量

继续在 **Variables** 标签页添加应用所需的环境变量：

#### 必须配置的变量（⚠️ 重要！）

```bash
# ==================== JWT 密钥（必须修改！）====================
JWT_SECRET_KEY=your-super-secret-jwt-key-here-minimum-32-characters-long
# 生成方法: python -c "import secrets; print(secrets.token_urlsafe(32))"

# ==================== Flask 密钥 ====================
SECRET_KEY=your-flask-secret-key-different-from-jwt-key

# ==================== 环境设置 ====================
FLASK_ENV=production
FLASK_DEBUG=False

# ==================== CORS 配置 ====================
CORS_ORIGINS=https://your-app-name.up.railway.app,http://localhost:3000

# ==================== 会话安全 ====================
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
```

#### 可选配置（使用默认值即可）

```bash
# 日志级别
LOG_LEVEL=info

# Worker 数量（Railway 免费版建议 1-2）
WORKERS=2

# 文件上传限制
MAX_CONTENT_LENGTH_MB=16
```

---

### 第5步：重新部署

添加完环境变量后：

1. 点击 **"Deployments"** 标签页
2. 点击最新的部署记录右侧的 **"Redeploy"** 按钮
3. 等待构建和启动完成（约1-2分钟）

---

## 🔧 环境变量配置详解

### 完整的环境变量清单

复制以下内容到 Railway 的 Variables 中（逐个添加）：

#### 数据库配置
```
DB_HOST=${{MySQL.HOST}}
DB_PORT=${{MySQL.PORT}}
DB_USER=${{MySQL.USER}}
DB_PASSWORD=${{MySQL.PASSWORD}}
DB_NAME=railway
DB_CHARSET=utf8mb4
```

#### 安全配置
```
JWT_SECRET_KEY=在这里粘贴你生成的随机密钥
SECRET_KEY=在这里粘贴另一个随机密钥
FLASK_ENV=production
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

#### CORS 配置
```
CORS_ORIGINS=https://你的应用名.up.railway.app
```

#### 服务器配置
```
HOST=0.0.0.0
PORT=${{PORT}}          # 不要修改这个！Railway 需要
WORKERS=2               # 免费版推荐 2 个
LOG_LEVEL=info
```

### 如何生成安全的 JWT 密钥？

**方法1：在线生成器**
访问 https://generate-secret.vercel.app/32

**方法2：Python 命令行**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**方法3：Railway 终端**
在 Railway Dashboard 中打开终端，运行上述命令

---

## 🗄️ 数据库配置（MySQL）

### 方案A：使用 Railway MySQL 插件（推荐 ✅）

**优点**:
- ✅ 免费（500小时/月）
- ✅ 自动备份
- ✅ 无需管理
- ✅ 内网连接，延迟低

**步骤**:
已在上方第3步详细介绍。

### 方案B：使用外部 MySQL 数据库

如果你有自己的云数据库（如阿里云 RDS、AWS RDS 等）：

1. 在 Railway Variables 中手动设置：
   ```
   DB_HOST=你的数据库地址
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=你的密码
   DB_NAME=erp_system
   ```

2. 确保数据库允许 Railway IP 访问（通常需要白名单）

### 初始化数据库表结构

Railway 部署后，首次访问会自动执行 `init_database()` 函数创建表。

如果需要导入初始数据：

**方法1：通过 Railway 终端**
1. 打开 Railway Dashboard
2. 点击 MySQL 服务 → **"Query"** 标签
3. 粘贴你的 SQL 脚本并执行

**方法2：通过代码初始化**
你的 `backend/config/database.py` 中的 `init_database()` 函数会在应用启动时自动建表。

---

## ❓ 常见问题解决

### Q1: 部署失败 "Module not found"
**原因**: 依赖未正确安装

**解决方案**:
1. 检查 `requirements.txt` 是否完整
2. 查看 Railway 构建日志（Build Logs）
3. 确保 `runtime.txt` 或 `nixpacks.toml` 存在

### Q2: 应用启动后报错 "Database connection failed"
**原因**: 数据库连接信息错误

**解决方案**:
1. 检查 Variables 中的 `DB_*` 变量是否正确
2. 如果使用 Railway MySQL，确认使用了 `${{MySQL.*}}` 引用
3. 测试数据库连接：在 MySQL 服务的 Query 标签中执行 `SELECT 1`

### Q3: 页面显示 502 Bad Gateway
**原因**: 应用未正常启动或端口监听错误

**解决方案**:
1. 检查 Deployments 日志中的错误信息
2. 确认 `PORT=${{PORT}}` 变量存在且未被覆盖
3. 查看 Gunicorn 启动日志

### Q4: 上传文件丢失（重启后）
**原因**: Railway 容器是无状态的，重启后文件会丢失

**解决方案**:
- **短期方案**: 使用 Railway Volume 持久化存储
- **长期方案**: 改用对象存储（如 AWS S3、阿里云 OSS）
- **推荐**: 将上传文件存储到外部服务

### Q5: CORS 跨域错误
**原因**: 前端域名未在白名单中

**解决方案**:
1. 在 CORS_ORIGINS 中添加前端域名
2. 格式: `https://your-app.up.railway.app,http://localhost:3000`

### Q6: 内存不足（OOM Killed）
**原因**: Railway 免费版内存有限（512MB）

**解决方案**:
1. 减少 WORKERS 数量（改为 1 或 2）
2. 在 Variables 中添加: `WORKERS=1`
3. 升级到付费计划获取更多资源

### Q7: 如何查看实时日志？
**方法**:
1. Railway Dashboard → Deployments → 点击最新部署
2. 点击 **"Logs"** 标签查看实时日志
3. 或使用 Railway CLI: `railway logs`

---

## ⚙️ 高级配置

### 自定义域名（HTTPS）

Railway 支持绑定自定义域名！

1. 在 Dashboard 中点击 **"Settings"** 
2. 选择 **"Networking"** 标签
3. 点击 **"Add Domain"**
4. 输入你的域名（如 `erp.yourdomain.com`）
5. 按提示配置 DNS 记录（CNAME 或 A 记录）
6. Railway 会自动提供 SSL 证书

**DNS 配置示例**:
```
类型: CNAME
名称: erp
值: cname.vercel-dns.com
```

### 持久化存储（Volume）

用于保存上传的文件：

1. 在 Dashboard 中点击 **"+"** → **"Volume"**
2. 名称设为 `uploads`
3. 挂载路径设为 `/app/backend/uploads`
4. 修改代码中的上传路径为 `/app/backend/uploads`

### 环境分离（开发/生产）

使用 Railway 的 **Projects** 功能：

1. 创建两个 Project：
   - `kunze-erp-dev` (开发环境)
   - `kunze-erp-prod` (生产环境)

2. 分别配置不同的环境变量
3. 开发环境可以启用 DEBUG 模式

### 自动化部署（CI/CD）

Railway 支持自动部署：

**触发条件**:
- 推送到 `main` 分支（默认）
- 推送到特定分支（可配置）
- 手动触发

**配置方法**:
1. Dashboard → Settings → Source
2. 选择部署分支
3. 可选：开启 PR Preview 部署

---

## 📊 监控和维护

### 查看监控指标
Railway Dashboard 提供：
- CPU 使用率
- 内存使用量
- 网络流量
- 请求数统计

### 设置告警（可选）
1. Dashboard → Settings → Alerts
2. 配置内存/CPU 阈值告警
3. 可接收邮件或 Slack 通知

### 备份数据库
Railway MySQL 自动每日备份，保留 7 天。
手动备份：Dashboard → MySQL 服务 → **"Backups"**

---

## 💰 费用说明

### Railway 免费额度（2024年）
- ✅ $5/月 免费额度
- ✅ 512MB RAM / 容器
- ✅ 500 小时运行时间/月
- ✅ 1 GB 数据库存储
- ✅ 自定义域名支持

### 本项目预估费用
- Web 应用: ~$2-3/月（基础套餐）
- MySQL 数据库: 包含在免费额度内
- **总计**: $0-5/月（根据使用情况）

> 💡 对于小型 ERP 系统，免费额度足够日常使用！

---

## 🚀 部署检查清单

部署完成后，逐一验证：

- [ ] 应用成功启动（无错误日志）
- [ ] 可以访问首页（返回 200 OK）
- [ ] 登录功能正常
- [ ] 数据库连接成功（数据能读写）
- [ ] API 接口可访问
- [ ] 文件上传/下载正常（注意：容器重启会丢失）
- [ ] HTTPS 正常工作（绿色锁头图标）
- [ ] 自定义域名可访问（如配置了）

---

## 🆘 获取帮助

### 官方文档
- Railway 文档: https://docs.railway.app
- Nixpacks 文档: https://nixpacks.com/docs

### 社区支持
- Railway Discord: https://discord.gg/railway
- GitHub Issues: https://github.com/railwayapp/issues

### 本项目问题
查看日志: Railway Dashboard → Deployments → Logs
检查配置: Variables 标签页
重新部署: Deployments → Redeploy

---

## 🎯 下一步

部署成功后，你可以：

1. ✅ **测试所有功能** - 确保一切正常运行
2. 🔗 **绑定自定义域名** - 让 URL 更专业
3. 📱 **分享给用户** - 开始使用系统
4. 📊 **设置监控** - 关注系统健康状态
5. 💾 **定期备份数据** - 确保数据安全

---

**恭喜！你的 Kunze ERP System 已经成功上线到 Railway 了！** 🎉🚄

访问地址: `https://你的应用名.up.railway.app`
