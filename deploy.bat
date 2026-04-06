@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

:: =====================================================
:: Kunze ERP System - Windows 快速部署脚本
:: 用法: deploy.bat [start|stop|restart|status|logs]
:: =====================================================

title Kunze ERP System - Deployment Manager

echo ========================================
echo   Kunze ERP System - 部署管理工具
echo ========================================
echo.

cd /d "%~dp0"

:: 检查参数
if "%1"=="" goto :show_help
if /i "%1"=="start" goto :start_services
if /i "%1"=="stop" goto :stop_services
if /i "%1"=="restart" goto :restart_services
if /i "%1"=="status" goto :show_status
if /i "%1"=="logs" goto :show_logs
if /i "%1"=="install" goto :install_deps
if /i "%1"=="dev" goto :run_dev
if /i "%1"=="help" goto :show_help
goto :show_help

:: ==================== 显示帮助 ====================
:show_help
echo.
echo 用法: %~nx0 {命令}
echo.
echo 命令:
echo   install    安装Python依赖 (pip install -r requirements.txt)
echo   start      启动生产服务器 (Gunicorn)
echo   stop       停止服务器
echo   restart    重启服务器
echo   status     查看服务状态
echo   logs       查看日志
echo   dev        启动开发环境 (Flask debug模式)
echo   help       显示此帮助信息
echo.
echo 示例:
echo   %~nx0 install     安装依赖
echo   %~nx0 dev         启动开发服务器
echo   %~nx0 start       启动生产服务器
goto :eof

:: ==================== 安装依赖 ====================
:install_deps
echo.
echo [*] 正在安装Python依赖...
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python未安装或未添加到PATH
    echo 请安装Python 3.8+: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 安装依赖
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo.
echo [✓] 依赖安装成功！
pause
goto :eof

:: ==================== 启动开发环境 ====================
:run_dev
echo.
echo [*] 启动开发环境...
echo.

:: 检查.env文件
if not exist ".env" (
    echo [警告] .env文件不存在，从.env.example复制...
    copy .env.example .env >nul
    echo 请编辑 .env 文件配置数据库连接等参数！
    pause
    exit /b 1
)

:: 设置环境变量
set FLASK_ENV=development
set FLASK_DEBUG=True

echo.
echo ==========================================
echo   开发模式启动中...
echo   访问地址: http://localhost:5000
echo   按 Ctrl+C 停止服务器
echo ==========================================
echo.

:: 启动Flask开发服务器
cd backend
python app.py
goto :eof

:: ==================== 启动生产服务器 ====================
:start_services
echo.
echo [*] 启动生产服务器...
echo.

:: 检查Gunicorn
gunicorn --version >nul 2>&1
if errorlevel 1 (
    echo [警告] Gunicorn未安装，正在安装...
    pip install gunicorn
)

:: 检查.env文件
if not exist ".env" (
    echo [错误] .env文件不存在！
    echo 请先运行: %~nx0 install
    pause
    exit /b 1
)

:: 创建必要目录
if not exist "uploads" mkdir uploads
if not exist "backend\logs" mkdir backend\logs

:: 设置环境变量
set FLASK_ENV=production
set FLASK_DEBUG=False

echo.
echo ==========================================
echo   生产模式启动中...
echo   访问地址: http://localhost:5000
echo   Worker数量: 自动检测CPU核心数
echo   按 Ctrl+C 停止服务器
echo ==========================================
echo.

:: 使用Gunicorn启动
cd backend
gunicorn --config ../gunicorn.conf.py app:app
goto :eof

:: ==================== 停止服务 ====================
:stop_services
echo.
echo [*] 正在停止服务...

:: 尝试停止Gunicorn进程
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

:: 尝试停止Flask进程
taskkill /FI "WINDOWTITLE eq Kunze*" /F >nul 2>&1

echo [✓] 服务已停止
pause
goto :eof

:: ==================== 重启服务 ====================
:restart_services
call :stop_services
timeout /t 2 /nobreak >nul
call :start_services
goto :eof

:: ==================== 显示状态 ====================
:show_status
echo.
echo ==========================================
echo   服务状态检查
echo ==========================================
echo.

:: 检查端口5000是否在监听
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo [状态] 服务未运行
) else (
    echo [状态] ✓ 服务正在运行
    echo.
    echo 监听端口: 5000
    netstat -ano | findstr ":5000" | findstr "LISTENING"
)

echo.
echo 系统资源:
tasklist | findstr /I "python gunicorn"

pause
goto :eof

:: ==================== 查看日志 ====================
:show_logs
echo.
echo [*] 显示最新日志...

if exist "backend\logs\system_*.log" (
    :: 找到最新的日志文件
    for /f "delims=" %%f in ('dir /b /o-d backend\logs\system_*.log 2^>nul') do (
        set LOGFILE=%%f
        goto :show_log_content
    )
    
    :show_log_content
    echo 最新日志文件: !LOGFILE!
    echo.
    type "backend\logs\!LOGFILE!" | more +0
) else (
    echo [警告] 未找到日志文件
    echo 日志目录: backend\logs\
)

pause
goto :eof

:eof
