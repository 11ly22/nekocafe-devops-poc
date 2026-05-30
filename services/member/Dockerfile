# ===== Stage 1: Dependencies =====
FROM node:20-alpine AS deps

WORKDIR /app

# 只复制 package 文件，最大化利用缓存
COPY package.json ./
RUN npm install --omit=dev && npm cache clean --force

# ===== Stage 2: Build =====
FROM node:20-alpine AS builder

WORKDIR /app
COPY package.json ./
RUN npm install  # 完整依赖（含 dev，用于构建阶段一致性）
COPY src/ ./src/

# ===== Stage 3: Runtime =====
FROM node:20-alpine AS runtime

# 安装 curl（健康检查用）
RUN apk add --no-cache curl

# 创建非 root 用户
RUN addgroup -g 10001 app && adduser -u 10001 -G app -D app

WORKDIR /app

# 从 deps 阶段复制生产依赖
COPY --from=deps /app/node_modules ./node_modules
# 从 builder 阶段复制应用代码
COPY --from=builder /app/src ./src
COPY package.json ./

RUN chown -R app:app /app

USER app

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/healthz || exit 1

CMD ["node", "src/index.js"]
