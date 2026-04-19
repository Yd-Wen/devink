# CLAUDE.md

本文档为 Claude Code (claude.ai/code) 在本项目中工作时提供指导。

## 项目概述

DevInk（研墨）是一个基于多智能体编排的 AI 博客写作助手。该系统协调多个 AI 智能体来生成博客文章——从标题生成、大纲创建、内容撰写到图片选择。项目包含 Vue 3 前端和 FastAPI 后端。

## 开发命令

### 前端 (Vue 3 + Vite)

```bash
cd frontend
npm install          # 安装依赖
npm run dev          # 启动开发服务器 (http://localhost:5173)
npm run build        # 构建生产版本
npm run type-check   # TypeScript 类型检查
```

### 后端 (FastAPI + Python 3.11+)

```bash
cd backend
# 激活虚拟环境 (如 .venv/Scripts/activate)
python -m app.main   # 启动服务器 (uvicorn, 热重载模式)
```

后端默认运行在 `http://localhost:8000`。API 文档位于 `/docs`。

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

- **OpenAI**：用于所有 AI 生成（标题、大纲、内容、图片分析）
- **MySQL**：主数据库
- **Redis**：会话缓存
- **阿里云 OSS**：图片存储
- **Pexels API**：库存图片搜索

## 数据库模型

主要实体：
- `User`：用户表
- `Blog`：博客文章，带状态（creating/completed/failed）
- `AgentLog**：AI 智能体执行日志