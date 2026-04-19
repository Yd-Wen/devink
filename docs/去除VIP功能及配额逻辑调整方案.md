# 去除VIP功能及配额逻辑调整方案

## 背景

原项目引入了VIP付费模式，普通用户只有5次配额且无法使用AI生图、SVG图表、AI修改大纲等高级功能。现在需要去除VIP功能，改为所有用户平等使用，仅通过每日配额进行频次控制。

## 用户确认的需求

1. **配额机制**：所有用户每日5次配额，创建博客时扣减，每天0点自动重置，管理员不受限制
2. **功能开放**：SVG图表、AI修改大纲对所有用户开放；**彻底删除NANO_BANANA配图方式**
3. **管理员**：保留admin角色，用于后台管理

## 后端修改

### 1. `backend/app/constants/user.py` — 删除VIP角色常量
- 删除 `VIP_ROLE = "vip"`
- `DEFAULT_QUOTA = 5` 保留

### 2. `backend/app/models/user.py` — 删除VIP时间字段
- 删除 `vip_time = Column("vipTime", DateTime, nullable=True, ...)` 字段
- `to_dict()` 方法中删除 `"vipTime"` 返回

### 3. `backend/app/models/enums.py` — 修正配图方式枚举
- `is_ai_generated()` 方法中 `ImageMethodEnum.SVG_DIAGRAM` 改为 `ImageMethodEnum.SVG`（原枚举中不存在 `SVG_DIAGRAM`，实际使用的是 `SVG`）
- `NANO_BANANA` 已被注释，无需额外处理

### 4. `backend/app/services/blog.py` — 核心逻辑改造
- **删除** `_default_non_vip_image_methods` 和 `_vip_only_image_methods` 两个集合
- **重写** `create_blog_task_with_quota_check`：
  - 管理员直接创建，不扣配额
  - 普通用户检查 `quota > 0`，扣减后创建
  - 配额不足时返回 `"今日配额已用完，每天 0 点自动恢复"`
- **删除** `ai_modify_outline` 中的VIP限制检查，所有用户可用
- **_is_vip_or_admin → _is_admin**：仅判断admin角色
- **_process_image_methods**：删除VIP默认配图逻辑，所有用户默认使用全部可用配图方式
- **_validate_image_methods**：删除VIP配图权限校验，同时删除NANO_BANANA相关校验

### 5. `backend/app/services/statistics.py` — 统计服务调整
- **删除** `_count_vip_users()` 方法
- **重写** `_calculate_quota_used()`：统计所有非admin用户的配额使用情况（原只统计普通用户，现在VIP角色已不存在）
- `get_statistics()` 中删除 `vip_user_count` 调用和传参

### 6. `backend/app/services/user.py` — 用户信息返回调整
- 删除 `vipTime` 相关返回（3处：登录、获取当前用户、添加用户等）
- 注册/添加用户时 quota 保持 `DEFAULT_QUOTA = 5`

### 7. `backend/app/schemas/statistics.py` — 删除VIP统计字段
- `StatisticsVO` 中删除 `vip_user_count` 字段（两处重复定义）

### 8. `backend/app/main.py` — 添加每日配额重置定时任务
- 使用 `asyncio` 后台任务实现，无需引入新依赖
- 在 `lifespan` 启动时创建后台任务
- 计算距离下一个0点的时间，sleep后执行重置
- 重置SQL：`UPDATE user SET quota = 5 WHERE userRole != 'admin'`
- 之后每24小时执行一次

## 前端修改

### 9. `frontend/src/constants/user.ts` — 删除VIP角色常量
- 删除 `export const USER_ROLE_VIP = 'vip'`

### 10. `frontend/src/utils/permission.ts` — 重写权限判断
- **删除** `isVip()` 函数
- **重写** `hasQuota()`：管理员返回 `true`，普通用户检查 `quota > 0`

### 11. `frontend/src/components/GlobalHeader.vue` — 删除VIP入口
- 删除顶部"升级VIP"按钮和"VIP"徽章
- 删除下拉菜单中的"永久会员权益"项
- 删除相关CSS样式（`.upgrade-vip-btn`、`.vip-badge`、`.vip-info-item`）

### 12. `frontend/src/pages/blog/BlogCreatePage.vue` — 创作页改造
- **配图方式**：删除 `NANO_BANANA` 复选框选项，删除所有VIP限制（SVG对所有用户开放）
- **删除** `vip-notice` 提示块和 `vip-icon` 皇冠图标
- **配额显示面板**：
  - 删除VIP会员"无限次"展示
  - 普通用户显示"今日剩余 X 次"，进度条保留
  - 管理员显示"无限次"
  - 添加提示文字"每天 0 点自动恢复"
- **创建按钮**：保留配额不足禁用逻辑
- **删除** `isVip` 计算属性和相关导入

### 13. `frontend/src/pages/blog/components/OutlineEditingStage.vue` — AI修改大纲开放
- 删除VIP限制，AI修改大纲功能对所有用户开放
- 删除 `vip-only`、`vip-badge-small`、`vip-upgrade-notice` 相关样式和条件渲染
- 保留AI输入框和按钮，无需条件判断

### 14. `frontend/src/pages/admin/StatisticsPage.vue` — 统计页面调整
- 删除"VIP会员数"统计卡片
- 删除"VIP用户"图表卡片
- 保留"配额使用情况"图表，但改为统计所有非admin用户

### 15. `frontend/src/api/typings.d.ts` — 删除VIP字段
- 删除 `vipUserCount: number` 字段定义

## 数据迁移说明

- **已有VIP用户**：去除VIP后，原VIP用户的 `userRole` 字段值为 `"vip"`，在 `_is_admin` 判断中不会被识别为管理员，因此会正常受每日5次配额限制。这是预期行为（所有用户平等）。
- **vipTime字段**：数据库中该字段会被忽略（模型删除后不再读写），不影响系统运行。如需清理，可后续单独执行ALTER TABLE删除。

## 验证步骤

1. 启动前后端服务
2. 用普通用户登录，确认：
   - 博客创建页显示"今日剩余 5 次"
   - 配图方式可选Pexels、Mermaid、Iconify、Emoji、SVG（无NANO_BANANA）
   - AI修改大纲功能可用
   - 创建博客后配额扣减为4
3. 用管理员登录，确认：
   - 显示"无限次"
   - 创建博客不扣减配额
4. 检查统计数据页面，确认无VIP相关统计
5. 确认全局头部无VIP相关按钮
