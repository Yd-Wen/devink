# 研墨 DevInk

<p align="center">
  <img src="frontend/src/assets/logo.png" alt="DevInk Logo" width="120">
</p>

<p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python"></a>
  <a href="https://vuejs.org"><img src="https://img.shields.io/badge/Vue-3.x-green.svg" alt="Vue"></a>
  <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-latest-teal.svg" alt="FastAPI"></a>
  <a href="#"><img src="https://img.shields.io/badge/AI-DashScope-orange.svg" alt="DashScope"></a>
  <a href="#vibe-coding"><img src="https://img.shields.io/badge/Built%20with-Vibe%20Coding-purple.svg" alt="Vibe Coding"></a>
</p>

<p align="center">基于多智能体编排的 AI 博客写作助手。通过协调多个 AI Agent 协作完成博客创作——从标题生成、大纲规划、内容撰写到配图搜索，提供完整的写作工作流，并通过 SSE 实时推送进度。</p>

- 仓库地址

  - [https://github.com/Yd-Wen/devink](https://github.com/Yd-Wen/devink)

  - [https://gitee.com/yindong-wen/devink](https://gitee.com/yindong-wen/devink)

- 项目地址：[https://devink.yindongwen.top](https://devink.yindongwen.top)

## 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue 3 + TypeScript + Vite + Ant Design Vue + Pinia + Vue Router + ECharts + Marked |
| **后端** | Python 3.11+ / FastAPI + SQLAlchemy + Redis + MySQL |
| **AI** | 阿里云 DashScope（通义千问 Qwen3-Max） |
| **基础设施** | Docker Compose / Nginx / MySQL 8.0 / Redis 7 |
| **配图服务** | Pexels 图库 / Mermaid 图表 / Iconify 图标 / Emoji 表情包 / SVG 示意图 |
| **对象存储** | 阿里云 OSS |

## 功能特性

- **多阶段 AI 写作流水线** — 标题生成（多方案）→ 大纲规划（可编辑）→ 正文撰写 + 配图搜索 → 合并为完整图文
- **SSE 实时进度推送** — 前后端通过 Server-Sent Events 长连接，实时展示各阶段生成状态
- **多 Agent 协作编排** — Title / Outline / Content / Image Analyzer / Merger 五个 Agent 分工协作
- **丰富的配图来源** — 支持 Pexels 免费图库、Mermaid 图表渲染、Iconify 图标、Emoji 表情包、SVG 示意图五种图片来源
- **用户配额管理** — 每日自动重置配额，管理员无限配额
- **管理员面板** — 用户管理、系统数据统计
- **Docker 一键部署** — 前后端 + MySQL + Redis 容器化，自动初始化数据库

## 项目结构

```
devink/
├── frontend/                   # Vue 3 前端
│   └── src/
│       ├── pages/              # 页面组件 (Home, Blog, User, Admin)
│       ├── components/         # 全局组件
│       ├── api/                # API 调用（从 OpenAPI 自动生成）
│       ├── stores/             # Pinia 状态管理
│       ├── router/             # Vue Router 路由配置
│       ├── utils/              # 工具函数 (SSE, Markdown, 权限等)
│       └── styles/             # CSS 样式
├── backend/                    # FastAPI 后端
│   └── app/
│       ├── routers/            # API 路由 (user, blog, health, statistics)
│       ├── services/           # 业务逻辑层
│       ├── agent/              # 多 Agent 系统
│       │   ├── orchestrator.py # Agent 编排器
│       │   ├── agents/         # 各 Agent 实现
│       │   ├── parallel/       # 并行图片生成
│       │   └── context/        # SSE 流式处理
│       ├── models/             # SQLAlchemy 数据模型
│       ├── schemas/            # Pydantic Schema
│       └── constants/          # 提示词模板、枚举
├── sql/                        # 数据库初始化脚本
├── docker-compose.yml          # Docker 容器编排
├── .env.example                # Docker 环境变量示例
└── CLAUDE.md                   # Claude Code 项目指南
```

## 安装部署

### 环境要求

- **前端**: Node.js 22.12+
- **后端**: Python 3.11+（推荐使用 `uv` 包管理器）
- **数据库**: MySQL 8.0 + Redis 7
- **可选**: Docker & Docker Compose（容器化部署）

### 环境变量配置

后端启动前需要配置 `backend/.env`，以下为关键环境变量：

| 变量 | 必填 | 说明 |
|------|:--:|------|
| `DB_HOST` | ✓ | MySQL 主机地址 |
| `DB_PORT` | | MySQL 端口，默认 `3306` |
| `DB_NAME` | ✓ | 数据库名称 |
| `DB_USER` | ✓ | 数据库用户名 |
| `DB_PASSWORD` | ✓ | 数据库密码 |
| `REDIS_HOST` | ✓ | Redis 主机地址 |
| `REDIS_PORT` | | Redis 端口，默认 `6379` |
| `REDIS_PASSWORD` | | Redis 密码，无密码留空 |
| `SESSION_SECRET_KEY` | ✓ | Session 加密密钥，生产环境请修改 |
| `PASSWORD_SALT` | ✓ | 密码加密盐值 |
| `INIT_ADMIN_PASSWORD` | | 种子用户初始密码，默认 `12345678` |
| `DASHSCOPE_API_KEY` | ✓ | 阿里云百炼 API Key |
| `DASHSCOPE_MODEL` | | AI 模型，默认 `qwen3-max` |
| `PEXELS_API_KEY` | ✓ | Pexels 图片搜索 API Key |
| `ALICLOUD_OSS_SECRET_ID` | ✓ | 阿里云 OSS AccessKey ID |
| `ALICLOUD_OSS_SECRET_KEY` | ✓ | 阿里云 OSS AccessKey Secret |
| `ALICLOUD_OSS_REGION` | ✓ | OSS 地域，如 `cn-hangzhou` |
| `ALICLOUD_OSS_BUCKET` | ✓ | OSS 存储桶名称 |

### API Key 获取

项目依赖以下外部服务，需要提前申请 API Key：

**1. DashScope（阿里云百炼）— AI 文本生成**

前往 [阿里云百炼控制台](https://bailian.console.aliyun.com) 开通 DashScope 服务，在 API Key 管理中创建 Key，模型推荐使用 `qwen3-max`。

**2. Pexels — 免费图库搜索**

前往 [Pexels API](https://www.pexels.com/api/) 注册账号并申请 API Key，用于博客配图搜索。

**3. 阿里云 OSS — 图片上传存储**

前往 [阿里云 RAM 控制台](https://ram.console.aliyun.com) 创建 AccessKey，并在 [OSS 控制台](https://oss.console.aliyun.com) 创建存储桶（Bucket），设置为公共读。

### 本地开发

**1. 克隆项目**

```bash
git clone https://github.com/Yd-Wen/devink.git
cd devink
```

**2. 启动后端**

```bash
cd backend
cp .env.example .env    # 编辑 .env 填入数据库、AI 等配置
uv sync                 # 安装依赖
uv run python ../sql/init_db.py --execute  # 初始化数据库
uv run python -m app.main  # 启动开发服务器 (http://localhost:8567)
```

**3. 启动前端**

```bash
cd frontend
npm install
npm run dev             # 启动开发服务器 (http://localhost:5173)
```

### Docker 部署

```bash
cp backend/.env.example backend/.env    # 编辑填入配置
cp .env.example .env                    # 编辑填入数据库密码
docker compose up -d                    # 启动所有服务
```

### Docker 常用命令

```bash
# 查看服务状态
docker compose ps

# 查看服务日志
docker compose logs -f backend    # 后端日志
docker compose logs -f frontend   # 前端日志
docker compose logs -f mysql      # 数据库日志

# 重启单个服务
docker compose restart backend

# 停止所有服务
docker compose down

# 停止并删除数据卷（清空数据）
docker compose down -v
```

服务启动后将自动执行数据库初始化，前端默认监听 80 端口，后端默认监听 8567 端口。

## 开源协议

本项目基于 [MIT](LICENSE) 协议开源。

Copyright (c) 2026 Yd Wen

## 作者

**Yd Wen** - [yindongwen.top](https://yindongwen.top)

## 致谢

- [ai-passage-creator](https://github.com/yuyuanweb/ai-passage-creator) — 参考来源，AI 文章生成
- [FastAPI](https://fastapi.tiangolo.com) — 高性能 Python Web 框架
- [Vue 3](https://vuejs.org) — 渐进式 JavaScript 前端框架
- [Vite](https://vitejs.dev) — 下一代前端构建工具
- [Ant Design Vue](https://antdv.com) — 企业级 UI 组件库
- [阿里云 DashScope](https://dashscope.aliyun.com) — AI 文本生成服务
- [Pexels](https://www.pexels.com) — 免费高质量图片资源

## 更新日志

### 2026-05-14
- ✨ **新增**: Docker 容器化部署
- 🔧 **杂项**: 更新 CLAUDE.md 项目指南

### 2026-05-12
- ✨ **新增**: 数据库初始化脚本
- 🎨 **优化**: 调整创作进度 UI
- 🎨 **优化**: 调整配图交互
- 🎨 **优化**: 调整 App Title

### 2026-05-11
- 🐛 **修复**: 大纲新增章节时列表渲染错误
- 🐛 **修复**: 配额获取错误
- 🎨 **优化**: 调整 message UI 全局配置
- 🔧 **杂项**: 更新配额刷新逻辑
- 🎨 **优化**: 更新 UI 和交互逻辑
- 🎨 **优化**: 更新 LOGO

### 2026-05-03
- 🐛 **修复**: 文章生成过程中的问题
- 🐛 **修复**: 注册登录配额错误

### 2026-04-20
- 🎨 **优化**: 统一前后端 API

### 2026-04-19
- ✨ **新增**: 统计分析模块
- ✨ **新增**: 多 Agent 编排
- ✨ **新增**: Agent 执行日志
- ✨ **新增**: 多配图方式扩展（Pexels / Mermaid / Iconify / Emoji / SVG）
- ✨ **新增**: 用户交互增强
- 🎨 **优化**: 去除 VIP 功能，调整配额逻辑
- 🎨 **优化**: 同步前后端 API、更新数据库脚本

### 2026-04-18
- ✨ **新增**: 前端项目初始化（Vue 3 + Vite）
- ✨ **新增**: 后端项目初始化（FastAPI）
- ✨ **新增**: 用户模块初始化（注册 / 登录 / 权限）
- ✨ **新增**: 博客模块（前后端）
- 🔧 **杂项**: 新增 .gitignore

<p align="center">
Made with ❤️ by DevInk Project
</p>
