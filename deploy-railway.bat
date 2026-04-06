@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

:: =====================================================
:: Kunze ERP System - Railway 快速部署助手
:: 帮助你一键完成 GitHub 推送和 Railway 部署准备
:: =====================================================

title Kunze ERP - Railway Deployment Helper

echo ══════════════════════════════════════════
echo   🚄 Kunze ERP System - Railway 部署助手
echo ══════════════════════════════════════════
echo.

cd /d "%~dp0"

:: 检查参数
if "%1"=="" goto :show_menu
if /i "%1"=="prepare" goto :prepare_deploy
if /i "%1"=="push" goto :push_to_github
if /i "%1"=="check" goto :check_config
if /i "%1"=="env" goto :show_env_template
if /i "%1"=="help" goto :show_help
goto :show_menu

:show_menu
echo.
echo 请选择操作:
echo.
echo   [1] 准备部署（检查配置并生成密钥）
echo   [2] 推送到 GitHub
echo   [3] 检查 Railway 配置文件
echo   [4] 显示环境变量模板
echo   [5] 完整部署流程（1+2）
echo   [0] 退出
echo.

set /p choice="请输入选项 (0-5): "

if "%choice%"=="1" goto :prepare_deploy
if "%choice%"=="2" goto :push_to_github
if "%choice%"=="3" goto :check_config
if "%choice%"=="4" goto :show_env_template
if "%choice%"=="5" goto :full_deploy
if "%choice%"=="0" goto :eof

echo 无效选项，请重新运行
pause
goto :show_menu

:prepare_deploy
echo.
echo [*] =======================================
echo   步骤 1/4: 检查项目配置
echo [*] =======================================

:: 检查必要文件
set MISSING_FILES=0

if not exist "requirements.txt" (
    echo [❌] 缺少 requirements.txt
    set /a MISSING_FILES+=1
) else (
    echo [✓] requirements.txt 存在
)

if not exist "Procfile" (
    echo [❌] 缺少 Procfile (Railway 启动文件)
    set /a MISSING_FILES+=1
) else (
    echo [✓] Procfile 存在
)

if not exist "railway.json" (
    echo [❌] 缺少 railway.json
    set /a MISSING_FILES+=1
) else (
    echo [✓] railway.json 存在
)

if not exist ".gitignore" (
    echo [❌] 缺少 .gitignore
    set /a MISSING_FILES+=1
) else (
    echo [✓] .gitignore 存在
)

if %MISSIVE_FILES% GTR 0 (
    echo.
    echo [错误] 缺少 %MISSIVE_FILES% 个必要文件！
    echo 请先运行完整的配置生成脚本。
    pause
    exit /b 1
)

echo.
echo [*] =======================================
echo   步骤 2/4: 生成安全密钥
echo [*] =======================================

:: 生成 JWT 密钥
echo 正在生成 JWT_SECRET_KEY...
for /f %%i in ('python -c "import secrets; print(secrets.token_urlsafe(32))"') do set JWT_KEY=%%i
echo [✓] JWT_SECRET_KEY 已生成: %JWT_KEY:~0,20%...

:: 生成 Flask 密钥
echo 正在生成 SECRET_KEY...
for /f %%i in ('python -c "import secrets; print(secrets.token_urlsafe(32))"') do set SECRET_KEY=%%i
echo [✓] SECRET_KEY 已生成: %SECRET_KEY:~0,20%...

echo.
echo [*] =======================================
echo   步骤 3/4: 创建 Railway 环境变量文件
echo [*] =======================================

(
echo # Railway 环境变量 - 自动生成于 %date% %time%
echo # 复制这些值到 Railway Dashboard → Variables
echo.
echo # ==================== 数据库配置 ====================
echo # 如果使用 Railway MySQL 插件，使用以下引用:
echo DB_HOST=${{MySQL.HOST}}
echo DB_PORT=${{MySQL.PORT}}
echo DB_USER=${{MySQL.USER}}
echo DB_PASSWORD=${{MySQL.PASSWORD}}
echo DB_NAME=${{MySQL.DATABASE}}
echo DB_CHARSET=utf8mb4
echo.
echo # ==================== 安全配置（已自动生成）====================
echo JWT_SECRET_KEY=%JWT_KEY%
echo SECRET_KEY=%SECRET_KEY%
echo JWT_ALGORITHM=HS256
echo JWT_EXPIRATION_HOURS=24
echo.
echo # ==================== Flask 配置 ====================
echo FLASK_ENV=production
echo FLASK_DEBUG=False
echo.
echo # ==================== CORS 配置 ====================
echo # 部署后替换为你的实际 URL:
echo CORS_ORIGINS=https://your-app-name.up.railway.app
echo.
echo # ==================== 会话安全 ====================
echo SESSION_COOKIE_SECURE=True
echo SESSION_COOKIE_HTTPONLY=True
echo SESSION_COOKIE_SAMESITE=Lax
echo.
echo # ==================== 服务器配置 ====================
echo HOST=0.0.0.0
echo PORT=${{PORT}}
echo WORKERS=2
echo LOG_LEVEL=info
) > railway-env-generated.txt

echo [✓] 环境变量已保存到 railway-env-generated.txt

echo.
echo [*] =======================================
echo   步骤 4/4: 检查 .gitignore
echo [*] =======================================

findstr /C:".env" .gitignore >nul 2>&1
if errorlevel 1 (
    echo [⚠️] 警告: .gitignore 中未排除 .env 文件
    echo 正在添加...
    echo .env >> .gitignore
    echo [✓] 已添加到 .gitignore
) else (
    echo [✓] .env 已在 .gitignore 中
)

findstr /C:"railway-env-generated.txt" .gitignore >nul 2>&1
if errorlevel 1 (
    echo railway-env-generated.txt >> .gitignore
    echo [✓] 已将 railway-env-generated.txt 添加到 .gitignore
)

echo.
echo ══════════════════════════════════════════
echo   ✅ 部署准备工作完成！
echo ══════════════════════════════════════════
echo.
echo 下一步:
echo   1. 运行 deploy-railway.bat push 推送到 GitHub
echo   2. 登录 https://railway.app
echo   3. 新建项目 → Deploy from GitHub repo
echo   4. 在 Variables 中粘贴 railway-env-generated.txt 的内容
echo   5. 添加 MySQL 服务（可选但推荐）
echo   6. 点击 Deploy Now
echo.
pause
goto :eof

:push_to_github
echo.
echo [*] 推送到 GitHub...
echo.

:: 检查 Git 是否初始化
if not exist ".git" (
    echo 正在初始化 Git 仓库...
    git init
    git add .
    git commit -m "Initial commit: Kunze ERP System with Railway config"
    
    echo.
    echo 请输入你的 GitHub 仓库地址:
    echo 示例: https://github.com/username/kunze_erp_system.git
    echo.
    set /p REPO_URL="GitHub 仓库地址: "
    
    if "!REPO_URL!"=="" (
        echo [错误] 仓库地址不能为空
        pause
        exit /b 1
    )
    
    git remote add origin !REPO_URL!
) else (
    git add .
    git commit -m "Update: Prepare for Railway deployment"
)

echo.
echo 正在推送到 GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo [❌] 推送失败！可能的原因:
    echo   1. 仓库地址不正确
    echo   2. 认证信息过期（请使用 GitHub CLI 或 SSH key）
    echo   3. 网络问题
    echo.
    echo 请检查后重试。
) else (
    echo.
    echo [✅] 成功推送到 GitHub！
    echo.
    echo 现在可以登录 Railway 进行部署了:
    echo   https://railway.app/new → Deploy from GitHub repo
)

pause
goto :eof

:check_config
echo.
echo [*] 检查 Railway 部署配置文件...
echo.

set CONFIG_OK=0

echo === 必需文件检查 ===
if exist "Procfile" (
    echo [✓] Procfile
    type Procfile
    set /a CONFIG_OK+=1
) else (
    echo [❌] Procfile 缺失
)

if exist "railway.json" (
    echo [✓] railway.json
    set /a CONFIG_OK+=1
) else (
    echo [❌] railway.json 缺失
)

if exist "runtime.txt" (
    echo [✓] runtime.txt
    type runtime.txt
    set /a CONFIG_OK+=1
) else (
    echo [❌] runtime.txt 缺失
)

if exist "nixpacks.toml" (
    echo [✓] nixpacks.toml
    set /a CONFIG_OK+=1
) else (
    echo [❌] nixpacks.toml 缺失
)

if exist "gunicorn.conf.py" (
    echo [✓] gunicorn.conf.py
    set /a CONFIG_OK+=1
) else (
    echo [❌] gunicorn.conf.py 缺失
)

echo.
echo === 检查结果: %CONFIG_OK%/5 个文件就绪 ===

if %CONFIG_OK% EQU 5 (
    echo [✅] 所有配置文件齐全，可以部署到 Railway！
) else (
    echo [⚠️]  缺少部分配置文件，建议先运行 prepare 命令
)

pause
goto :eof

:show_env_template
echo.
echo ══════════════════════════════════════════
echo   Railway 环境变量模板
echo ══════════════════════════════════════════
echo.
echo 复制以下内容到 Railway Dashboard → Variables:
echo.
echo ────────────────────────────────────────
type railway.env.example
echo ────────────────────────────────────────
echo.
echo 提示:
echo   - 使用 ${} 引用 Railway MySQL 变量
echo   - 必须修改 JWT_SECRET_KEY 和 SECRET_KEY
echo   - PORT 变量不要修改（Railway 动态分配）
echo.
pause
goto :eof

:full_deploy
call :prepare_deploy
if errorlevel 1 (
    echo [错误] 准备阶段失败
    pause
    exit /b 1
)
call :push_to_github
goto :eof

:show_help
echo.
echo 用法: %~nx0 {命令}
echo.
echo 命令:
echo   prepare     准备部署（检查配置、生成密钥）
echo   push        推送到 GitHub
echo   check       检查 Railway 配置文件
echo   env         显示环境变量模板
echo   full        完整部署流程（prepare + push）
echo   help        显示此帮助
echo.
echo 示例:
echo   %~nx0           # 显示菜单
echo   %~nx0 prepare   # 准备部署
echo   %~nx0 full      # 一键完成所有步骤
echo.
pause
goto :eof

:eof
