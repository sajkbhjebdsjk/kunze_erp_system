# 🚀 Kunze ERP System - 部署操作手册

> **当前状态**: ✅ 代码已准备就绪，等待推送到 GitHub
> 
> **你的信息**:
> - 👤 GitHub 用户名: sajkbhjebdsjk
> - 📧 邮箱: 2632090182@qq.com
> - 📦 仓库名称: kunze_erp_system
> - 🔑 JWT密钥: lTBkWm8-z1Owc10rlhaTRAFckTwvb0eSIoGm5RVQogA
> - 🔑 Flask密钥: bivLlZDnXMytwkKbQRY-s04j4ZlZztbBSowFUVmu6a8

---

## ✅ 已完成的准备工作

- [x] 检查项目配置文件（Procfile、railway.json 等）
- [x] 生成安全密钥（JWT + Flask）
- [x] 初始化 Git 仓库
- [x] 配置 Git 用户信息（张鹏材 / 2632090182@qq.com）
- [x] 创建首次提交（83个文件）
- [x] 配置远程仓库地址

---

## 🔥 第1步：推送到 GitHub（现在执行）

### 方法A：使用 Git 命令行（推荐）

打开 **Git Bash** 或 **命令提示符**，进入项目目录：

```bash
cd C:\Users\26320\Desktop\kunze_erp_system
```

然后执行：

```bash
# 1. 查看当前状态
git status

# 2. 推送到 GitHub（会弹出登录窗口或要求输入token）
git push -u origin main
```

**如果提示登录**：
- 会弹出一个浏览器窗口让你授权 GitHub
- 或者提示输入 **Personal Access Token**（不是密码！）

### 方法B：使用 GitHub Desktop（图形界面，最简单）

1. 下载安装 **GitHub Desktop**: https://desktop.github.com/
2. 打开 GitHub Desktop
3. 点击 **"File" → "Add local repository"**
4. 选择文件夹：`C:\Users\26320\Desktop\kunze_erp_system`
5. 点击 **"Publish repository"** （发布仓库）
6. 选择 GitHub 账号：sajkbhjebdsjk
7. 仓库名：`kunze_erp_system`
8. 保持 **Private**（私有）或改为 **Public**（公开）
9. 点击 **"Publish repository"**

### 方法C：直接上传到 GitHub 网页（最简单但慢）

1. 打开浏览器访问：https://github.com/sajkbhjebdsjk/kunze_erp_system
2. 点击 **"uploading an existing file"**
3. **拖拽整个 `kunze_erp_system` 文件夹**到上传区域
4. 等待上传完成（可能需要几分钟）
5. 点击 **"Commit changes"**

---

## ⚠️ 重要：GitHub 不再支持密码登录！

如果你在 `git push` 时遇到认证错误，需要生成 **Personal Access Token**:

### 生成 Token 步骤（1分钟）：

1. 登录 GitHub：https://github.com
2. 点击右上角头像 → **Settings**
3. 左侧菜单最下方 → **Developer settings**
4. 点击 **Personal access tokens** → **Tokens (classic)**
5. 点击 **Generate new token** → **Generate new token (classic)**
6. 设置：
   - **Note**: `Kunze ERP Deploy`
   - **Expiration**: 选择 90 days 或 No expiration
   - **勾选权限**: `repo` (第一个，勾选全部子项)
7. 点击 **Generate token**
8. **复制生成的 token**（只显示一次！）

### 使用 Token 推送：

```bash
git push -u origin main
# 当提示输入密码时，粘贴上面的 token（不是GitHub密码）
```

---

## 🚄 第2步：部署到 Railway（推送成功后）

### 2.1 注册/登录 Railway

1. 访问：https://railway.app
2. 点击 **"Get Started"** 或 **"Login with GitHub"** ✅ **推荐用GitHub登录！**

### 2.2 创建新项目

1. 登录后点击 **"New Project"** 或 **"+"** 按钮
2. 选择 **"Deploy from GitHub repo"**

### 2.3 选择仓库并部署

1. 在仓库列表中找到并选择：**kunze_erp_system**
2. 点击 **"Deploy Now"**
3. Railway 会自动检测 Python 项目并开始构建（约2-3分钟）

### 2.4 添加环境变量（重要！⚠️）

**构建完成后必须配置环境变量**，否则应用无法启动！

1. 在 Railway Dashboard 中，点击你的项目
2. 点击顶部的 **"Variables"** 标签
3. 点击 **"+ New"** 逐个添加以下变量：

#### 必须添加的变量（从 `railway-env-generated.txt` 复制）：

```
变量名                          值
─────────────────────────────────────────────────
JWT_SECRET_KEY                  lTBkWm8-z1Owc10rlhaTRAFckTwvb0eSIoGm5RVQogA
SECRET_KEY                      bivLlZDnXMytwkKbQRY-s04j4ZlZztbBSowFUVmu6a8
FLASK_ENV                       production
FLASK_DEBUG                     False
CORS_ORIGINS                    https://你的应用名.up.railway.app
HOST                            0.0.0.0
PORT                            ${{PORT}}
WORKERS                         2
LOG_LEVEL                       info
SESSION_COOKIE_SECURE           True
SESSION_COOKIE_HTTPONLY         True
```

#### 如果添加了 MySQL 数据库（推荐）：

```
变量名                          值
─────────────────────────────────────────────────
DB_HOST                         ${{MySQL.HOST}}
DB_PORT                         ${{MySQL.PORT}}
DB_USER                         ${{MySQL.USER}}
DB_PASSWORD                     ${{MySQL.PASSWORD}}
DB_NAME                         ${{MySQL.DATABASE}}
DB_CHARSET                      utf8mb4
```

### 2.5 添加 MySQL 数据库（可选但强烈推荐）

1. 在项目中点击 **"+"** 按钮
2. 选择 **"Database"** → **"MySQL"**
3. 等待创建完成（30秒）
4. 上面的 DB_* 变量就可以使用了

### 2.6 重新部署

添加完环境变量后：

1. 点击 **"Deployments"** 标签
2. 找到最新的部署记录
3. 点击右侧 **"⋮"** 菜单 → **"Redeploy"**
4. 等待重新部署完成（1-2分钟）

---

## 🎉 第3步：访问你的应用

部署成功后：

1. 在 Dashboard 中点击你的 Web 服务
2. 找到 **"Public URL"** 或 **"Domain"** 
3. 点击链接访问你的应用！

URL 格式通常是：`https://你的应用名.up.railway.app`

---

## ✅ 部署验证清单

部署完成后，逐一测试：

- [ ] 应用启动成功（无报错日志）
- [ ] 可以访问首页（显示登录页面）
- [ ] 可以登录系统（默认账号或你创建的账号）
- [ ] 数据库连接正常（数据能读写）
- [ ] API 接口可访问
- [ ] 文件上传功能正常
- [ ] HTTPS 正常工作（浏览器地址栏有🔒图标）

---

## ❓ 常见问题快速解决

### Q1: 推送时提示 "Authentication failed"
**A**: GitHub 不再支持密码！需要使用 Personal Access Token（见上方说明）

### Q2: Railway 构建失败 "Module not found"
**A**: 检查 `requirements.txt` 是否完整，查看 Build Logs

### Q3: 应用启动失败 "Database connection failed"
**A**: 检查 Variables 中的 DB_* 变量是否正确

### Q4: 页面显示 502 Bad Gateway
**A**: 确保 PORT 变量设置为 `${{PORT}}`（不要改成数字！）

### Q5: 内存不足被杀死 (OOM Killed)
**A**: 在 Variables 中设置 `WORKERS=1`（免费版只有512MB内存）

### Q6: 如何查看日志？
**A**: Railway Dashboard → Deployments → 点击最新部署 → Logs 标签

---

## 📞 需要帮助？

- 📘 **详细教程**: 查看 `RAILWAY_DEPLOYMENT.md`
- 🌐 **Railway 官方文档**: https://docs.railway.app
- 💬 **Railway Discord 社区**: https://discord.gg/railway
- 🐛 **本项目的环境变量**: 查看 `railway-env-generated.txt`

---

## 🎯 下一步

部署成功后，你可以：

1. ✅ **绑定自定义域名** - 让URL更专业
2. 📱 **分享给团队成员** - 开始使用系统
3. 📊 **设置监控告警** - 关注系统健康
4. 💾 **定期备份数据** - Railway MySQL自动备份

---

**祝你部署顺利！如有问题随时问我** 😊🚀
