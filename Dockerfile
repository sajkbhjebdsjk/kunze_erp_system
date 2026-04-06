# =====================================================
# Kunze ERP System - 生产环境Docker配置
# 构建命令: docker build -t kunze-erp-system .
# 运行命令: docker run -p 5000:5000 --env-file .env kunze-erp-system
# =====================================================

# 阶段1：基础镜像
FROM python:3.10-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装Python包
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY rider-contract-sign.html ./

# 创建必要的目录
RUN mkdir -p /app/backend/uploads \
    /app/backend/logs \
    /app/uploads

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" || exit 1

# 使用Gunicorn运行生产服务器
CMD ["gunicorn", "--config", "gunicorn.conf.py", "backend.app:app"]
