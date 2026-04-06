# =====================================================
# Kunze ERP System - 生产环境Docker配置
# 适用于: Railway / Docker / 本地部署
# =====================================================

# 阶段1：基础镜像
FROM python:3.10-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 设置工作目录（重要：必须是 backend 目录才能正确导入模块）
WORKDIR /app/backend

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装Python包（包含 gunicorn）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn==21.2.0

# 复制应用代码到正确位置
COPY backend/ ./
COPY ../frontend/ ./frontend/
COPY ../rider-contract-sign.html ./
COPY ../gunicorn.conf.py ./

# 创建必要的目录
RUN mkdir -p uploads logs

# 暴露端口
EXPOSE 5000

# 使用Gunicorn运行生产服务器（在 backend 目录下）
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
