# CLAUDE.md

本文档为 Claude Code (claude.ai/code) 在本项目中工作时提供指导。

## 项目概述

DevInk（研墨）是一个基于多智能体编排的 AI 博客写作助手。该系统协调多个 AI 智能体来生成博客文章——从标题生成、大纲创建、内容撰写到图片选择。项目包含 Vue 3 前端和 FastAPI 后端。

## 开发命令

### 前端 (Vue 3 + Vite)

```bash
cd frontend
npm install           # 安装依赖
npm run dev           # 启动开发服务器 (http://localhost:5173)
npm run build         # TypeScript 类型检查 + 生产构建
npm run type-check    # 仅 TypeScript 类型检查 (vue-tsc)
npm run format        # Prettier 格式化 src/
npm run openapi2ts    # 从后端 OpenAPI 自动生成 API 类型 (src/api/)
```

### 后端 (FastAPI + Python 3.11+)

项目使用 `uv` 作为包管理器（`pyproject.toml` + `uv.lock`）。

```bash
cd backend
uv sync                        # 安装/同步依赖（自动创建 .venv）
uv run python -m app.main      # 启动开发服务器 (uvicorn, 热重载)
uv run black app/              # 格式化代码
uv run pytest                  # 运行测试
```

后端默认运行在 `http://localhost:8567`（端口由 `SERVER_PORT` 环境变量控制）。

### 数据库初始化

```bash
# 使用 Python 脚本（推荐）
# 读取 backend/.env 配置， 对密码进行加密，最好执行 SQL 脚本
cd backend && uv run python ../sql/init_db.py --execute

# 或手动执行 SQL 脚本
mysql -u root -p < sql/init.sql
```

### Docker 部署

```bash
# 配置环境变量（参考 backend/.env.example 和 .env.example）
cp backend/.env.example backend/.env
cp .env.example .env

# 启动所有服务（前端、后端、MySQL、Redis）
docker compose up -d

# 查看日志
docker compose logs -f backend
```

Docker 启动流程：`entrypoint.sh` 等待 MySQL/Redis 就绪 → 执行 `sql/init_db.py` 初始化数据库 → 启动 uvicorn。

## 架构

### 后端结构

```
backend/app/
├── main.py                    # FastAPI 应用入口, lifespan, CORS, 路由注册
├── config.py                  # 配置项 (database, redis, openai)
├── database.py                # SQLAlchemy 数据库连接
├── depends.py                 # 依赖注入
├── exceptions.py              # BusinessException, ErrorCode
├── routers/                   # API 端点
│   ├── user.py
│   ├── blog.py
│   └── health.py
├── services/                  # 业务逻辑
│   ├── user.py
│   ├── blog.py
│   ├── blog_async.py
│   ├── blog_agent.py          # 博客写作编排服务
│   └── image_*.py             # 图片服务 (pexels, mermaid, iconify, emoji, svg)
├── models/                    # SQLAlchemy 模型
├── schemas/                   # Pydantic schema
├── agent/                     # 多智能体系统
│   ├── orchestrator.py        # 协调所有智能体
│   ├── agents/                # 各个智能体
│   │   ├── title_generator.py
│   │   ├── outline_generator.py
│   │   ├── content_generator.py
│   │   ├── image_analyzer.py
│   │   └── merger.py
│   ├── parallel/
│   │   └── image_generator.py
│   └── context/
│       └── stream_handler.py  # SSE 流式处理
└── constants/                 # 提示词模板, 枚举
```

**后端核心模式：**
- 路由 → 服务 → 模型架构
- 多阶段博客生成：阶段 1（标题）→ 阶段 2（大纲）→ 阶段 3（内容 + 图片 + 合并）
- SSE (Server-Sent Events) 用于实时进度更新
- Redis 用于会话管理
- MySQL 用于持久化存储
- 多种图片来源：Pexels（照片）、Mermaid（图表）、Iconify（图标）、Emoji、SVG

### 前端结构

```
frontend/src/
├── main.ts                    # 应用入口
├── App.vue                    # 根组件
├── router/index.ts            # Vue Router 配置
├── stores/loginUser.ts        # Pinia 状态管理
├── api/                       # API 调用 (从 OpenAPI 自动生成)
├── pages/
│   ├── HomePage.vue
│   ├── user/                  # 登录、注册
│   └── blog/                  # BlogListPage, BlogCreatePage, BlogDetailPage
│       └── components/        # 博客创建流程的状态组件
├── components/                # 全局组件
├── utils/                     # 工具函数 (permission, markdown, sse, date)
├── constants/                 # 常量
└── styles/                    # CSS 样式
```

## 配置

- 后端：`backend/app/config.py` - 使用 pydantic-settings，从环境变量读取
- 前端：`frontend/src/config/env.ts` - API 基础 URL 配置
- 前后端均提供了环境变量示例文件

## 关键集成

- **DashScope（阿里云百炼）**：AI 生成服务。通过 OpenAI 兼容客户端调用（`openai` 库连接 DashScope 端点），模型默认为 `qwen3-max`。用于标题、大纲、正文生成及图片分析。
- **MySQL 8.0**：主数据库（`sql/init.sql` 提供建表与种子数据）
- **Redis 7**：Session 缓存
- **阿里云 OSS**：图片上传存储
- **Pexels API**：免费图库搜索
- **Mermaid CLI**：将 Mermaid 代码渲染为 SVG 图片（需要 Node.js + Chromium）

## 数据库模型

主要实体：
- `User`：用户表
- `Blog`：博客文章，带状态（creating/completed/failed）
- `AgentLog`：AI 智能体执行日志（记录每次智能体调用的耗时、prompt、输入输出）

## 博客生成流程（SSE 流式架构）

博客创建是分阶段的异步流水线，前端通过 SSE 实时接收进度：

1. **POST** `/api/blog` 提交选题 → 返回 `taskId`
2. 前端连接 **GET** `/api/blog/progress/{taskId}`（SSE 长连接，`text/event-stream`）
3. 后端通过 `blog_agent.py` 编排，依次执行：
   - 阶段 1：标题生成（3-5 个方案，用户选择）
   - 阶段 2：大纲生成（用户可编辑）
   - 阶段 3：正文生成 + 配图搜索/生成 + 合并为完整图文
4. 每个阶段完成后推送 `TITLE_READY` / `OUTLINE_READY` / `PHASE_CHANGE` 事件
5. 前端 `utils/sse.ts` 解析事件流，博客创建页组件根据 `phase` 渲染对应 UI

关键实现细节：
- `orchestrator.py` 协调所有智能体（title/outline/content/image_analyzer/merger）
- `parallel/image_generator.py` 并发生成多种来源的配图（Pexels/Mermaid/Iconify/Emoji/SVG）
- `context/stream_handler.py` 封装 SSE 消息推送
- Nginx 反代需要禁用 SSE 路径的缓冲（`proxy_buffering off`，已在 `nginx.conf` 配置）

## API 约定

所有 API 响应统一使用 `{ code, data, message }` 信封格式：
- `code: 0` 表示成功，其他值见 `ErrorCode` 枚举
- 业务异常通过 `BusinessException` 抛出，由全局 `exception_handler` 捕获
- SSE 路径错误返回 `text/event-stream` 格式以维持连接