# DevInk Docker 容器化部署方案

## 部署方式推荐

DevInk 包含 4 个运行时组件（Nginx+前端、FastAPI 后端、MySQL、Redis），推荐以下两种部署方式：

| 方案 | 适用场景 | 复杂度 | 运维成本 |
|---|---|---|---|
| **Docker Compose**（推荐） | 单服务器部署、中小流量 | 低 | 低 |
| Kubernetes | 多服务器集群、大流量、需自动扩缩容 | 高 | 高 |

对于本项目当前规模，**Docker Compose 是最佳选择**——一键编排所有服务，配置简单，迁移到任何云服务器只需 `docker compose up -d` 一条命令。下文详述此方案。

---

## 一、架构概览

```
                     ┌──────────────────────────────────────┐
  用户 :80 ─────────→│  Nginx (frontend 容器)                │
                     │  /          → SPA 静态文件            │
                     │  /api/*     → 反向代理到 backend:8567 │
                     └──────────┬───────────────────────────┘
                                │
                     ┌──────────▼───────────────────────────┐
                     │  FastAPI (backend 容器) :8567         │
                     │  - 等待 MySQL/Redis 就绪               │
                     │  - 执行 init_db.py 初始化数据库        │
                     │  - 启动 uvicorn (无热重载)             │
                     └──────┬─────────────┬─────────────────┘
                            │             │
               ┌────────────▼──┐  ┌───────▼──────────────┐
               │  MySQL :3306  │  │  Redis :6379          │
               │  (官方镜像)    │  │  (alpine 镜像)        │
               └───────────────┘  └──────────────────────┘
```

核心设计：
- **同源部署**：Nginx 提供前端静态文件 + 反向代理 `/api`，前后端同源，无需 CORS
- **SSE 支持**：Nginx 关闭代理缓冲，超时设为 3600s，确保博客生成进度长连接不断
- **健康检查**：所有服务配置 healthcheck，启动顺序由依赖健康状态保证
- **数据持久化**：MySQL 和 Redis 通过 Docker volume 保存数据

---

## 二、新建文件

需要新增以下 8 个文件：

### 2.1 `docker-compose.yml`（项目根目录）

```yaml
version: "3.8"

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        VITE_API_BASE_URL: ${VITE_API_BASE_URL:-/api}
    container_name: devink-frontend
    ports:
      - "${NGINX_PORT:-80}:80"
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - devink-net
    restart: unless-stopped

  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: devink-backend
    ports:
      - "${BACKEND_PORT:-8567}:8567"
    env_file:
      - backend/.env
    environment:
      # 覆盖 .env 中的这些值，适配 Docker 网络
      DB_HOST: mysql
      REDIS_HOST: redis
      ALLOWED_ORIGINS: ""
      SERVER_HOST: "0.0.0.0"
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - devink-net
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8567/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  mysql:
    image: mysql:8.0
    container_name: devink-mysql
    ports:
      - "${MYSQL_PORT:-3306}:3306"
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD:-root}
      MYSQL_DATABASE: ${DB_NAME:-devink}
      MYSQL_ROOT_HOST: "%"
    volumes:
      - mysql_data:/var/lib/mysql
    command: >
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_unicode_ci
      --default-authentication-plugin=mysql_native_password
    networks:
      - devink-net
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p$$MYSQL_ROOT_PASSWORD"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  redis:
    image: redis:7-alpine
    container_name: devink-redis
    ports:
      - "${REDIS_PORT:-6379}:6379"
    volumes:
      - redis_data:/data
    networks:
      - devink-net
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  mysql_data:
    driver: local
  redis_data:
    driver: local

networks:
  devink-net:
    driver: bridge
```

### 2.2 `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

# 系统依赖：Chromium（Mermaid CLI 需要）+ Node.js（安装 mmdc 需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    libasound2 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    curl \
    fonts-noto-cjk \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 安装 Node.js 22.x（用于 mermaid-cli）
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# 安装 mermaid-cli（提供 mmdc 命令）
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
RUN npm install -g @mermaid-js/mermaid-cli

# 安装 uv 包管理器
RUN pip install uv

WORKDIR /app

# 先复制依赖文件，利用 Docker 缓存
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev

# 复制应用代码和数据库初始化脚本
COPY backend/ ./
COPY sql/ ./sql/

# 将 uv 虚拟环境的 bin 加入 PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8567

# 启动脚本
COPY backend/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
```

### 2.3 `backend/entrypoint.sh`

```bash
#!/bin/bash
set -e

echo "==> Waiting for MySQL at ${DB_HOST}:${DB_PORT}..."
until python -c "
import pymysql
pymysql.connect(host='${DB_HOST}', port=${DB_PORT}, user='${DB_USER}', password='${DB_PASSWORD}')
print('connected')
" 2>/dev/null; do
    sleep 2
done
echo "==> MySQL is ready."

echo "==> Waiting for Redis at ${REDIS_HOST}:${REDIS_PORT}..."
until python -c "
import redis
r = redis.Redis(host='${REDIS_HOST}', port=${REDIS_PORT}, decode_responses=True)
r.ping()
" 2>/dev/null; do
    sleep 2
done
echo "==> Redis is ready."

# 初始化数据库
echo "==> Running database initialization..."
python sql/init_db.py --execute
echo "==> Database initialized."

# 启动应用
echo "==> Starting FastAPI server..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8567 --no-access-log
```

### 2.4 `backend/.dockerignore`

```
__pycache__/
*.pyc
*.pyo
.venv/
.env
.git/
.gitignore
.python-version
README.md
*.egg-info/
dist/
build/
```

### 2.5 `frontend/Dockerfile`

```dockerfile
# ===== Stage 1: 构建 =====
FROM node:22-alpine AS build

ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . ./
RUN npm run build

# ===== Stage 2: 运行 =====
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 2.6 `frontend/nginx.conf`

```nginx
upstream backend {
    server backend:8567;
}

server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript image/svg+xml;
    gzip_min_length 1024;
    gzip_proxied any;

    # API 反向代理
    location /api/ {
        proxy_pass http://backend/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE 支持（博客生成进度推送）
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding on;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }

    # SPA fallback：非文件、非 API 路由返回 index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存（Vite 构建输出带内容哈希）
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 2.7 `frontend/.dockerignore`

```
node_modules/
dist/
.vscode/
*.local
.env
.env.*
!env.d.ts
.git/
.gitignore
README.md
```

### 2.8 `frontend/.env.production`

```
VITE_API_BASE_URL=/api
```

---

## 三、修改现有文件

### 3.1 `backend/app/config.py` — 新增 CORS 配置项

在 `Settings` 类中添加（约第 18 行，`server_host` 之后）：

```python
# CORS 配置：逗号分隔的允许来源，空字符串表示不启用 CORS（同源部署）
allowed_origins: str = "http://localhost:5173"
```

### 3.2 `backend/app/main.py` — CORS 配置化 + 移除热重载

**修改 1**：将第 64–71 行的硬编码 CORS 改为从配置读取：

```python
# CORS 配置（从环境变量读取，空字符串 = 不启用 = 同源部署）
origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

**修改 2**：将第 136 行的 `reload=True` 移除：

```python
# 改前:
uvicorn.run("app.main:app", host=settings.server_host, port=settings.server_port, reload=True)

# 改后:
uvicorn.run("app.main:app", host=settings.server_host, port=settings.server_port)
```

### 3.3 `sql/init_db.py` — 兼容系统环境变量

`load_env()` 函数当前在 `.env` 文件不存在时直接退出。Docker 中环境变量由 docker-compose 注入，不依赖 `.env` 文件。修改逻辑为：

```python
def load_env(env_path: Path) -> dict[str, str]:
    """加载环境变量，优先从 .env 文件，否则从系统环境变量（Docker 场景）"""
    if env_path.exists():
        try:
            from dotenv import dotenv_values
            return dotenv_values(str(env_path))
        except ImportError:
            pass
        env = {}
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip().strip("\"'")
        return env

    # 回退：从系统环境变量读取（Docker 场景）
    import os
    env = {}
    required_keys = [
        "PASSWORD_SALT", "INIT_ADMIN_PASSWORD",
        "DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME"
    ]
    for key in required_keys:
        if key in os.environ:
            env[key] = os.environ[key]
    return env
```

`_execute_sql()` 函数（第 87 行附近）同样需要处理 `.env` 不存在的场景——将第 95 行的 `env = load_env(BACKEND_ENV)` 改为能从系统环境变量回退即可。`DB_HOST` 等默认值已经在 `env.get()` 中提供了 fallback。

### 3.4 `frontend/src/config/env.ts` — 使用 Vite 环境变量

当前本地配置（`env.ts` 在 `.gitignore` 中，每人不提交），内容需改为：

```typescript
// API 基础地址
// 构建时通过 VITE_API_BASE_URL 注入，开发时默认 localhost:8567
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8567/api'
```

`frontend/src/config/env.example.ts` 同步更新为：

```typescript
/**
 * 环境变量配置示例
 * 复制此文件为 env.ts 并填写实际配置
 *
 * 开发环境: VITE_API_BASE_URL=http://localhost:8567/api
 * Docker 生产环境: VITE_API_BASE_URL=/api（通过 Nginx 反向代理）
 */

// API 基础地址
// import.meta.env.VITE_API_BASE_URL 在构建时由 Vite 静态替换
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8567/api'
```

---

## 四、关键设计决策

### 为什么前端容器内嵌 Nginx 而不是单独 Nginx 服务？

减少服务数量（4 个而非 5 个）。前端只有静态文件，Nginx 放在同一容器是 SPA 的标准做法——一个 `nginx:alpine` 镜像仅增加约 5MB，换来更简单的编排和调试。

### 为什么用 backend entrypoint 初始化数据库而不是 MySQL 的 /docker-entrypoint-initdb.d？

`init.sql` 需要运行时变量替换——用 `PASSWORD_SALT` 和 `INIT_ADMIN_PASSWORD` 计算 MD5 哈希填入 SQL。MySQL 初始化机制只能执行静态 SQL 文件，无法做模板替换。由后端 entrypoint 执行 `init_db.py` 可保证密码哈希正确。

### 为什么用 `uv sync --frozen` 而不是 `pip install`？

项目使用 `uv` 包管理器，已有 `uv.lock` 锁定文件。`uv sync --frozen` 等同于 `npm ci`，从 lock 文件精确还原依赖版本，避免 "在我机器上能跑" 的问题。

### Mermaid CLI 为什么需要 Chromium？

`@mermaid-js/mermaid-cli` 内部使用 Puppeteer 启动无头浏览器渲染图表为 SVG/PNG。利用 `PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium` 复用系统 Chromium，避免重复下载。

---

## 五、使用指南

### 前置条件

- 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/) 或 Docker Engine + Docker Compose v2
- 确保 `backend/.env` 文件已填写所有必填配置（API Key、OSS 凭证等）

### 开发环境 vs Docker 环境的变量差异

Docker Compose 会**自动覆盖**以下变量（通过 `environment:` 字段），无需修改 `.env`：

| 变量 | .env 中的值（开发） | Docker 中强制值 | 原因 |
|---|---|---|---|
| `DB_HOST` | localhost / 127.0.0.1 | `mysql` | 容器间用服务名通信 |
| `REDIS_HOST` | localhost | `redis` | 同上 |
| `ALLOWED_ORIGINS` | （无此配置，需新增） | `""`（空） | 同源部署无需 CORS |

### 构建与启动

```bash
# 在项目根目录执行

# 首次部署：构建并后台启动所有服务
docker compose up -d --build

# 查看运行状态
docker compose ps

# 查看后端日志
docker compose logs -f backend
```

### 验证部署

```bash
# 1. 所有容器健康
docker compose ps
# 期望：4 个服务状态为 "Up" 且 "(healthy)"

# 2. API 健康检查
curl http://localhost/api/health
# 期望：{"code": 0, "data": "OK", "message": "服务正常"}

# 3. 前端可访问
curl -I http://localhost/
# 期望：HTTP/1.1 200 OK

# 4. 确认数据库初始化成功
docker compose logs backend | grep "init.sql"
# 期望：[OK] SQL 已成功执行到 mysql:3306/devink

# 5. SPA fallback 正常（任意前端路径不返回 404）
curl -I http://localhost/create
# 期望：HTTP/1.1 200 OK（返回 index.html）
```

### 日常运维

```bash
# 代码更新后重新构建后端
docker compose up -d --build backend

# 前端更新后重新构建
docker compose up -d --build frontend

# 查看所有日志
docker compose logs -f

# 停服
docker compose down

# 停服并清空数据库（危险！）
docker compose down -v
```

---

## 六、云服务器部署

### 以阿里云 ECS / 腾讯云 CVM 为例

1. 在服务器上安装 Docker：
```bash
curl -fsSL https://get.docker.com | bash
```

2. 将项目代码上传至服务器（git clone 或 scp）

3. 确保 `backend/.env` 已填写生产环境配置

4. 执行 `docker compose up -d --build`

5. 配置云服务器安全组，开放 80 端口（以及 HTTPS 443 如果使用）

### HTTPS 建议

在云服务器上部署后，建议在前面加一层 **Nginx Proxy Manager** 或 **Caddy** 处理 SSL 证书（Let's Encrypt 自动续期），将 443 端口流量转发到 Docker Compose 的 80 端口。

---

## 七、常见问题

**Q: 前端构建时如何修改 API 地址？**
```bash
# 默认 /api（同源），如需自定义前缀：
VITE_API_BASE_URL=/devink/api docker compose build --build-arg VITE_API_BASE_URL=/devink/api frontend
```

**Q: 如何调试后端？**
```bash
# 进入容器
docker compose exec backend bash

# 手动执行数据库初始化
python sql/init_db.py --execute

# 检查 Mermaid CLI
mmdc --version
chromium --version
```

**Q: MySQL 数据如何备份？**
```bash
docker compose exec mysql mysqldump -u root -p devink > backup.sql
```

**Q: 启动顺序如何保证？**
docker-compose.yml 中通过 `depends_on` + `condition: service_healthy` 保证 MySQL 和 Redis 先启动并通过健康检查后，backend 才启动；backend healthy 后 frontend 才启动。
