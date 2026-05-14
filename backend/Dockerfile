FROM python:3.11-slim

# 替换为阿里云镜像源（国内服务器加速）
RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources \
    && sed -i 's|security.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources

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

# 安装 mermaid-cli（提供 mmdc 命令），复用系统 Chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
RUN npm config set registry https://registry.npmmirror.com \
    && npm install -g @mermaid-js/mermaid-cli

# 安装 uv 包管理器
RUN pip install uv -i https://mirrors.aliyun.com/pypi/simple/

WORKDIR /app

# 先复制依赖文件，利用 Docker 缓存层
COPY backend/pyproject.toml backend/uv.lock backend/README.md ./
ENV UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
RUN uv sync --frozen --no-dev

# 复制应用代码和数据库初始化脚本
COPY backend/ ./
COPY sql/ ./sql/

# 将 uv 虚拟环境的 bin 加入 PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8567

COPY backend/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
