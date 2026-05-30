# ===== Stage 1: Builder =====
FROM python:3.12-slim AS builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装 Python 依赖（利用 Docker 层缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 复制应用代码与测试（便于容器内 make test）
COPY src/ ./src/
COPY tests/ ./tests/

# ===== Stage 2: Runtime =====
FROM python:3.12-slim AS runtime

# 创建非 root 用户（安全基线要求）
RUN groupadd -r app && useradd -r -g app -u 10001 app

WORKDIR /app

# 从 builder 阶段复制已安装的依赖
COPY --from=builder /root/.local /home/app/.local
COPY --from=builder /app/src ./src
COPY --from=builder /app/tests ./tests

# setuptools 供 OpenTelemetry 使用（安装到 app 用户 site-packages）
RUN pip install --no-cache-dir --target=/home/app/.local/lib/python3.12/site-packages setuptools

# 调整文件所有权
RUN chown -R app:app /app

USER app

# 最小化攻击面：不暴露不必要的端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/healthz')"

# 启动命令
ENV PATH=/home/app/.local/bin:$PATH
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
