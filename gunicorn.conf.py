import os
import sys
import multiprocessing

# =====================================================
# 关键修复：将 backend 目录添加到 Python 搜索路径
# 解决 Docker/Railway 环境下的模块导入问题
# =====================================================
_backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
if _backend_path not in sys.path:
    sys.path.insert(0, _backend_path)

# =====================================================
# Gunicorn 配置 - 适配 Railway / Docker / 传统部署
# 自动检测运行环境并调整配置
# =====================================================

# 检测是否在 Railway 环境中
is_railway = os.environ.get('RAILWAY_ENVIRONMENT', '') != ''
is_docker = os.path.exists('/.dockerenv') or os.environ.get('KUBERNETES_SERVICE_HOST', '')

# ==================== 服务器绑定地址 ====================
# Railway 会动态分配 PORT 变量（必须使用！）
host = os.environ.get('HOST', '0.0.0.0')
port = int(os.environ.get('PORT', '5000'))
bind = f"{host}:{port}"

# ==================== Worker进程配置 ====================
# Railway 推荐使用较少 workers（免费额度有限）
if is_railway:
    workers = int(os.environ.get('WORKERS', '2'))  # Railway 免费版建议 1-2 个
    worker_class = 'sync'
    threads = 1
    print(f"✓ Railway 环境检测: Workers={workers}, Threads={threads}")
else:
    cpu_count = multiprocessing.cpu_count()
    workers = int(os.environ.get('WORKERS', str(cpu_count * 2 + 1)))
    worker_class = os.environ.get('WORKER_CLASS', 'sync')
    threads = int(os.environ.get('THREADS', '2'))

timeout = 120
keepalive = 5

# ==================== Worker重启配置 ====================
max_requests = 1000          # 防止内存泄漏
max_requests_jitter = 50     # 避免同时重启
preload_app = True           # 预加载应用

# ==================== 日志配置 ====================
accesslog = '-'              # 输出到 stdout（Railway/Docker 日志收集）
errorlog = '-'
loglevel = os.environ.get('LOG_LEVEL', 'info')

# 访问日志格式
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ==================== 安全配置 ====================
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190

# ==================== 进程配置 ====================
proc_name = 'kunze_erp_system'
pidfile = None              # 容器环境不需要 pidfile

# 权限设置
user = None
group = None
umask = 0o027              # 八进制整数格式（文件权限掩码）

# 优雅关闭超时
graceful_timeout = 30


def on_starting(server):
    """Gunicorn启动时的回调"""
    env_type = "Railway ☁️" if is_railway else ("Docker 🐳" if is_docker else "Local 💻")
    
    print("=" * 60)
    print(f"🚀 Kunze ERP System - Production Server [{env_type}]")
    print(f"   Bind: {bind}")
    print(f"   Workers: {workers}")
    print(f"   Worker Class: {worker_class}")
    print(f"   Threads: {threads}")
    print(f"   Log Level: {loglevel}")
    
    if is_railway:
        railway_url = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
        if railway_url:
            print(f"   🔗 URL: https://{railway_url}")
        else:
            print(f"   🌐 URL: Check Railway Dashboard for public URL")
    
    print("=" * 60)


def post_fork(server, worker):
    """Worker fork后的回调"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def worker_int(worker):
    """Worker收到INT信号"""
    worker.log.info("Worker received INT signal")


def worker_abort(worker):
    """Worker异常退出"""
    worker.log.info("Worker aborted (pid: %s)", worker.pid)


def pre_exec(server):
    """Fork前执行"""
    server.log.info("Forked child, re-executing.")


def when_ready(server):
    """服务器就绪时触发"""
    if is_railway:
        print("\n✅ Server is ready and accepting connections on Railway!")
        print("   Check your Railway Dashboard for the public URL\n")
