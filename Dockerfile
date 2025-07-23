# VerbaAurea Document Processing API Dockerfile
# 多阶段构建，优化镜像大小

# 第一阶段：构建阶段
FROM python:3.11-slim as builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements-api.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --user -r requirements-api.txt

# 第二阶段：运行阶段
FROM python:3.11-slim

# 创建非root用户
RUN groupadd -r verba && useradd -r -g verba verba

# 设置工作目录
WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制Python包
COPY --from=builder /root/.local /home/verba/.local

# 复制应用代码
COPY . .

# 设置Python路径
ENV PATH=/home/verba/.local/bin:$PATH
ENV PYTHONPATH=/app

# 创建必要的目录
RUN mkdir -p /tmp/verba_aurea_uploads /tmp/verba_aurea_outputs \
    && chown -R verba:verba /app /tmp/verba_aurea_uploads /tmp/verba_aurea_outputs

# 切换到非root用户
USER verba

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# 启动命令
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
