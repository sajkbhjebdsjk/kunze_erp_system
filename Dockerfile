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

# 设置工作目录为项目根目录
WORKDIR /app

# 安装系统依赖（包含中文字体支持）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    fontconfig \
    fonts-wqy-zenhei \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /app/backend/fonts \
    && wget -q --timeout=30 -O /app/backend/fonts/NotoSansSC-Regular.ttf \
       "https://raw.githubusercontent.com/AaronFeng753/chinese-fonts/main/fonts/simsun.ttf" \
    || echo "[WARN] Font download failed, will use system fonts" \
    && fc-cache -fv

# 复制依赖文件并安装Python包（包含 gunicorn）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn==21.2.0

# 复制所有应用代码（使用绝对路径，不用 ../）
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY rider-contract-sign.html ./
COPY gunicorn.conf.py ./

# 创建必要的目录
RUN mkdir -p ./backend/uploads ./backend/logs ./uploads

# 暴露端口
EXPOSE 5000

# 使用Gunicorn运行生产服务器
# 从 /app 目录启动，指定 backend.app:app
CMD ["gunicorn", "--config", "gunicorn.conf.py", "backend.app:app"]
