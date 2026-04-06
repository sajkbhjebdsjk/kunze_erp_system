# 🚄 Railway 一键部署 - 5分钟上线！

> **最简单的部署方式**：无需服务器，免费额度，自动HTTPS

## ✨ 为什么选择 Railway？

- ✅ **零配置**：自动检测 Python 项目
- ✅ **免费额度**：$5/月（足够小型项目）
- ✅ **自动 HTTPS**：自带 SSL 证书
- ✅ **自动扩展**：按需扩容
- ✅ **全球 CDN**：快速访问
- ✅ **一键部署**：从 GitHub 直接部署

---

## ⚡ 3步完成部署

### 第1步：准备代码（1分钟）

```bash
# Windows 用户:
deploy-railway.bat prepare

# Linux/Mac 用户:
chmod +x deploy-railway.sh
./deploy-railway.sh prepare
```

这会：
- ✅ 检查所有必需文件
- ✅ 自动生成安全密钥
- ✅ 创建环境变量配置文件

### 第2步：推送到 GitHub（2分钟）

```bash
# Windows:
deploy-railway.bat push

# Linux/Mac:
./deploy-railway.sh push
```

或手动执行：
```bash
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### 第3步：在 Railway 部署（2分钟）

1. 访问 https://railway.app/new
2. 点击 **"Deploy from GitHub repo"**
3. 选择 `kunze_erp_system` 仓库
4. 点击 **"Deploy Now"**
5. 等待 2-3 分钟...

**🎉 完成！** 你的应用已上线：`https://你的应用名.up.railway.app`

---

## 🔧 配置数据库（推荐）

Railway 提供免费 MySQL：

1. 在 Dashboard 点击 **"+"**
2. 选择 **"Database" → "MySQL"**
3. 等待创建完成（30秒）
4. 在 Variables 中添加：
   ```
   DB_HOST=${{MySQL.HOST}}
   DB_PORT=${{MySQL.PORT}}
   DB_USER=${{MySQL.USER}}
   DB_PASSWORD=${{MySQL.PASSWORD}}
   DB_NAME=${{MySQL.DATABASE}}
   ```

详细说明见 [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)

---

## 📋 必须设置的环境变量

在 Railway Dashboard → Variables 中添加：

```bash
# 安全密钥（运行 deploy-railway.bat prepare 会自动生成）
JWT_SECRET_KEY=你的随机密钥
SECRET_KEY=另一个随机密钥

# 环境
FLASK_ENV=production
FLASK_DEBUG=False

# CORS（替换为你的实际URL）
CORS_ORIGINS=https://你的应用.up.railway.app

# 服务器（不要修改 PORT！）
HOST=0.0.0.0
PORT=${{PORT}}
WORKERS=2
```

完整变量列表见 [railway.env.example](./railway.env.example)

---

## 🚀 常用命令

```bash
# 完整部署流程（推荐新用户使用）
deploy-railway.bat full          # Windows
./deploy-railway.sh full         # Linux/Mac

# 分步骤执行
deploy-railway.bat prepare       # 准备配置和生成密钥
deploy-railway.bat push          # 推送到 GitHub
deploy-railway.bat check         # 检查配置是否正确
deploy-railway.bat env           # 查看环境变量模板
```

---

## ❓ 遇到问题？

### 查看日志
Railway Dashboard → Deployments → 点击最新部署 → **Logs**

### 常见错误

| 错误 | 解决方案 |
|------|----------|
| Module not found | 检查 requirements.txt |
| Database connection failed | 检查 DB_* 环境变量 |
| 502 Bad Gateway | 检查 PORT 变量是否为 `${{PORT}}` |
| Memory OOM | 减少 WORKERS 为 1 |

更多问题解答：[RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md#常见问题解决)

---

## 💰 费用预估

| 资源 | 免费额度 | 本项目预估 |
|------|----------|-----------|
| Web 应用 | $5/月 | ~$0-3/月 |
| MySQL | 500h/月 | 包含在免费额度 |
| 存储 | 1GB | 够用 |
| 流量 | 无限 | 无限制 |

**总计：$0-5/月**（大多数情况免费！）

---

## 📚 更多资源

- 📘 **完整教程**: [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)
- 🌐 **Railway 官方文档**: https://docs.railway.app
- 💬 **Railway Discord**: https://discord.gg/railway
- 🐛 **问题反馈**: GitHub Issues

---

## ✅ 部署检查清单

部署完成后验证：

- [ ] 应用成功启动（无报错日志）
- [ ] 可以访问首页（200 OK）
- [ ] 登录功能正常
- [ ] 数据库连接成功
- [ ] API 接口可访问
- [ ] HTTPS 正常工作（绿色🔒图标）

---

**🎊 恭喜！你的 ERP 系统已经在线上运行了！**

立即访问: `https://你的应用名.up.railway.app`
