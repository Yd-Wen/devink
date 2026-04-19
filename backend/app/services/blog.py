"""博客服务"""

import json
import logging
import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from databases import Database
from sqlalchemy import and_, func, select

from app.exceptions import BusinessException, ErrorCode, throw_if, throw_if_not
from app.constants.user import UserConstant
from app.models.blog import Blog
from app.models.enums import BlogPhaseEnum, BlogStatusEnum, ImageMethodEnum
from app.schemas.blog import (
    BlogQueryRequest,
    BlogState,
    BlogVO,
    OutlineSection,
    TitleOption,
)
from app.schemas.user import LoginUserVO
from app.services.blog_agent import BlogAgentService

logger = logging.getLogger(__name__)


class BlogService:
    """博客服务"""

    def __init__(self, db: Database):
        self.db = db
        self._default_non_vip_image_methods = [
            ImageMethodEnum.PEXELS.value,
            ImageMethodEnum.MERMAID.value,
            ImageMethodEnum.ICONIFY.value,
            ImageMethodEnum.EMOJI_PACK.value,
        ]
        self._vip_only_image_methods = {
            ImageMethodEnum.NANO_BANANA.value,
            ImageMethodEnum.SVG_DIAGRAM.value,
        }

    async def create_blog_task(
        self,
        topic: str,
        login_user: LoginUserVO,
        style: Optional[str] = None,
        enabled_image_methods: Optional[List[str]] = None,
    ) -> str:
        """创建博客任务"""
        final_image_methods = self._process_image_methods(enabled_image_methods, login_user)
        self._validate_image_methods(final_image_methods, login_user)

        task_id = str(uuid.uuid4())
        now = datetime.now()
        query = """
            INSERT INTO blog (
                taskId, userId, topic, style, enabledImageMethods, status, phase, createTime
            )
            VALUES (
                :taskId, :userId, :topic, :style, :enabledImageMethods, :status, :phase, :createTime
            )
        """
        await self.db.execute(
            query=query,
            values={
                "taskId": task_id,
                "userId": login_user.id,
                "topic": topic,
                "style": style,
                "enabledImageMethods": json.dumps(final_image_methods, ensure_ascii=False)
                if final_image_methods
                else None,
                "status": BlogStatusEnum.PENDING.value,
                "phase": BlogPhaseEnum.PENDING.value,
                "createTime": now,
            },
        )
        logger.info("博客任务创建成功, taskId=%s, userId=%s", task_id, login_user.id)
        return task_id

    async def create_blog_task_with_quota_check(
        self,
        topic: str,
        login_user: LoginUserVO,
        style: Optional[str] = None,
        enabled_image_methods: Optional[List[str]] = None,
    ) -> str:
        """在同一事务中完成配额扣减和任务创建"""
        if self._is_vip_or_admin(login_user):
            return await self.create_blog_task(
                topic=topic,
                login_user=login_user,
                style=style,
                enabled_image_methods=enabled_image_methods,
            )

        async with self.db.transaction():
            quota_row = await self.db.fetch_one(
                query="""
                    SELECT quota
                    FROM user
                    WHERE id = :userId AND isDelete = 0
                    FOR UPDATE
                """,
                values={"userId": login_user.id},
            )
            throw_if_not(quota_row, ErrorCode.NOT_FOUND_ERROR, "用户不存在")
            throw_if(quota_row["quota"] <= 0, ErrorCode.OPERATION_ERROR, "配额不足")

            await self.db.execute(
                query="""
                    UPDATE user
                    SET quota = quota - 1
                    WHERE id = :userId
                """,
                values={"userId": login_user.id},
            )

            return await self.create_blog_task(
                topic=topic,
                login_user=login_user,
                style=style,
                enabled_image_methods=enabled_image_methods,
            )

    async def get_by_task_id(self, task_id: str):
        """根据任务 ID 查询博客记录"""
        query = select(Blog).where(and_(Blog.task_id == task_id, Blog.is_delete == 0))
        return await self.db.fetch_one(query)

    async def get_blog_detail(self, task_id: str, login_user: LoginUserVO) -> BlogVO:
        """获取博客详情"""
        blog = await self.get_by_task_id(task_id)
        throw_if_not(blog, ErrorCode.NOT_FOUND_ERROR, "博客不存在")
        self._check_blog_permission(blog, login_user)
        return self._to_blog_vo(blog)

    async def list_blog_by_page(
        self,
        request: BlogQueryRequest,
        login_user: LoginUserVO,
    ) -> Tuple[List[BlogVO], int]:
        """分页查询博客列表"""
        conditions = [Blog.is_delete == 0]
        if login_user.user_role != "admin":
            conditions.append(Blog.user_id == login_user.id)

        if request.id:
            conditions.append(Blog.id == request.id)
        if request.task_id:
            conditions.append(Blog.task_id == request.task_id)
        if request.user_id:
            conditions.append(Blog.user_id == request.user_id)
        if request.topic:
            conditions.append(Blog.topic.like(f"%{request.topic}%"))
        if request.status:
            conditions.append(Blog.status == request.status)

        count_query = select(func.count(Blog.id)).where(and_(*conditions))
        total = await self.db.fetch_val(count_query)

        query = (
            select(Blog)
            .where(and_(*conditions))
            .order_by(Blog.create_time.desc())
            .limit(request.page_size)
            .offset((request.current - 1) * request.page_size)
        )
        blogs = await self.db.fetch_all(query)
        return [self._to_blog_vo(blog) for blog in blogs], total

    async def delete_blog(self, blog_id: int, login_user: LoginUserVO) -> bool:
        """删除博客"""
        query = select(Blog).where(and_(Blog.id == blog_id, Blog.is_delete == 0))
        blog = await self.db.fetch_one(query)
        throw_if_not(blog, ErrorCode.NOT_FOUND_ERROR, "博客不存在")
        self._check_blog_permission(blog, login_user)
        await self.db.execute(query="UPDATE blog SET isDelete = 1 WHERE id = :id", values={"id": blog_id})
        return True

    async def update_blog_status(
        self,
        task_id: str,
        status: BlogStatusEnum,
        error_message: Optional[str] = None,
    ):
        """更新博客状态"""
        if status == BlogStatusEnum.COMPLETED:
            await self.db.execute(
                query="""
                    UPDATE blog
                    SET status = :status, completedTime = :completedTime
                    WHERE taskId = :taskId
                """,
                values={
                    "status": status.value,
                    "completedTime": datetime.now(),
                    "taskId": task_id,
                },
            )
            return

        if status == BlogStatusEnum.FAILED:
            await self.db.execute(
                query="""
                    UPDATE blog
                    SET status = :status, errorMessage = :errorMessage
                    WHERE taskId = :taskId
                """,
                values={
                    "status": status.value,
                    "errorMessage": error_message,
                    "taskId": task_id,
                },
            )
            return

        await self.db.execute(
            query="UPDATE blog SET status = :status WHERE taskId = :taskId",
            values={"status": status.value, "taskId": task_id},
        )

    async def update_phase(self, task_id: str, phase: BlogPhaseEnum):
        """更新博客阶段"""
        blog = await self.get_by_task_id(task_id)
        if not blog:
            logger.error("博客记录不存在, taskId=%s", task_id)
            return

        current_phase_value = blog["phase"] or BlogPhaseEnum.PENDING.value
        try:
            current_phase = BlogPhaseEnum(current_phase_value)
        except ValueError as exc:
            raise BusinessException(ErrorCode.OPERATION_ERROR, "当前阶段非法") from exc
        if current_phase != phase and not current_phase.can_transition_to(phase):
            raise BusinessException(ErrorCode.OPERATION_ERROR, "非法阶段流转")

        await self.db.execute(
            query="UPDATE blog SET phase = :phase WHERE taskId = :taskId",
            values={"phase": phase.value, "taskId": task_id},
        )

    async def save_title_options(self, task_id: str, title_options: List[TitleOption]):
        """保存标题方案列表"""
        await self.db.execute(
            query="UPDATE blog SET titleOptions = :titleOptions WHERE taskId = :taskId",
            values={
                "taskId": task_id,
                "titleOptions": json.dumps(
                    [item.model_dump(by_alias=True) for item in title_options],
                    ensure_ascii=False,
                ),
            },
        )

    async def confirm_title(
        self,
        task_id: str,
        selected_main_title: str,
        selected_sub_title: str,
        user_description: Optional[str],
        login_user: LoginUserVO,
    ):
        """确认标题并进入大纲阶段"""
        blog = await self.get_by_task_id(task_id)
        throw_if_not(blog, ErrorCode.NOT_FOUND_ERROR, "博客不存在")
        self._check_blog_permission(blog, login_user)
        throw_if(
            blog["phase"] != BlogPhaseEnum.TITLE_SELECTING.value,
            ErrorCode.OPERATION_ERROR,
            "当前阶段不允许确认标题",
        )

        await self.db.execute(
            query="""
                UPDATE blog
                SET mainTitle = :mainTitle,
                    subTitle = :subTitle,
                    userDescription = :userDescription,
                    phase = :phase
                WHERE taskId = :taskId
            """,
            values={
                "taskId": task_id,
                "mainTitle": selected_main_title,
                "subTitle": selected_sub_title,
                "userDescription": user_description,
                "phase": BlogPhaseEnum.OUTLINE_GENERATING.value,
            },
        )

    async def confirm_outline(
        self,
        task_id: str,
        outline: List[OutlineSection],
        login_user: LoginUserVO,
    ):
        """确认大纲并进入正文阶段"""
        blog = await self.get_by_task_id(task_id)
        throw_if_not(blog, ErrorCode.NOT_FOUND_ERROR, "博客不存在")
        self._check_blog_permission(blog, login_user)
        throw_if(
            blog["phase"] != BlogPhaseEnum.OUTLINE_EDITING.value,
            ErrorCode.OPERATION_ERROR,
            "当前阶段不允许确认大纲",
        )

        await self.db.execute(
            query="""
                UPDATE blog
                SET outline = :outline,
                    phase = :phase
                WHERE taskId = :taskId
            """,
            values={
                "taskId": task_id,
                "outline": json.dumps([item.model_dump() for item in outline], ensure_ascii=False),
                "phase": BlogPhaseEnum.CONTENT_GENERATING.value,
            },
        )

    async def save_outline(self, task_id: str, outline: List[OutlineSection]):
        """保存大纲内容（不推进阶段）"""
        await self.db.execute(
            query="UPDATE blog SET outline = :outline WHERE taskId = :taskId",
            values={
                "taskId": task_id,
                "outline": json.dumps([item.model_dump() for item in outline], ensure_ascii=False),
            },
        )

    async def ai_modify_outline(
        self,
        task_id: str,
        modify_suggestion: str,
        login_user: LoginUserVO,
    ) -> List[OutlineSection]:
        """AI 修改大纲"""
        blog = await self.get_by_task_id(task_id)
        throw_if_not(blog, ErrorCode.NOT_FOUND_ERROR, "博客不存在")
        self._check_blog_permission(blog, login_user)
        throw_if(
            not self._is_vip_or_admin(login_user),
            ErrorCode.NO_AUTH_ERROR,
            "AI 修改大纲功能仅限 VIP 会员使用",
        )
        throw_if(
            blog["phase"] != BlogPhaseEnum.OUTLINE_EDITING.value,
            ErrorCode.OPERATION_ERROR,
            "当前阶段不允许 AI 修改大纲",
        )
        throw_if(not blog["outline"], ErrorCode.OPERATION_ERROR, "当前博客尚未生成大纲")

        current_outline = [OutlineSection(**item) for item in json.loads(blog["outline"])]
        agent_service = BlogAgentService()
        modified_outline = await agent_service.ai_modify_outline(
            task_id=task_id,
            main_title=blog["mainTitle"],
            sub_title=blog["subTitle"],
            current_outline=current_outline,
            modify_suggestion=modify_suggestion,
        )
        await self.db.execute(
            query="UPDATE blog SET outline = :outline WHERE taskId = :taskId",
            values={
                "taskId": task_id,
                "outline": json.dumps(
                    [item.model_dump() for item in modified_outline],
                    ensure_ascii=False,
                ),
            },
        )
        return modified_outline

    async def save_blog_content(self, task_id: str, state: BlogState):
        """保存博客内容"""
        cover_image = None
        if state.images:
            cover = next((img for img in state.images if img.position == 1), None)
            if cover and cover.url:
                cover_image = cover.url

        await self.db.execute(
            query="""
                UPDATE blog
                SET mainTitle = :mainTitle,
                    subTitle = :subTitle,
                    outline = :outline,
                    content = :content,
                    fullContent = :fullContent,
                    coverImage = :coverImage,
                    images = :images
                WHERE taskId = :taskId
            """,
            values={
                "taskId": task_id,
                "mainTitle": state.title.main_title if state.title else None,
                "subTitle": state.title.sub_title if state.title else None,
                "outline": json.dumps([s.model_dump() for s in state.outline.sections], ensure_ascii=False)
                if state.outline
                else None,
                "content": state.content,
                "fullContent": state.full_content,
                "coverImage": cover_image,
                "images": json.dumps([img.model_dump(by_alias=True) for img in state.images], ensure_ascii=False)
                if state.images
                else None,
            },
        )

    def _check_blog_permission(self, blog, login_user: LoginUserVO):
        """检查博客访问权限"""
        if blog["userId"] != login_user.id and login_user.user_role != UserConstant.ADMIN_ROLE:
            raise BusinessException(ErrorCode.NO_AUTH_ERROR, "无权限访问")

    def _is_vip_or_admin(self, login_user: LoginUserVO) -> bool:
        """是否为 VIP 或管理员"""
        return login_user.user_role in {UserConstant.ADMIN_ROLE, UserConstant.VIP_ROLE}

    def _process_image_methods(
        self,
        enabled_image_methods: Optional[List[str]],
        login_user: LoginUserVO,
    ) -> Optional[List[str]]:
        """处理配图方式默认值"""
        if enabled_image_methods:
            return enabled_image_methods

        if self._is_vip_or_admin(login_user):
            return None

        return list(self._default_non_vip_image_methods)

    def _validate_image_methods(
        self,
        enabled_image_methods: Optional[List[str]],
        login_user: LoginUserVO,
    ):
        """校验普通用户高级配图权限"""
        if not enabled_image_methods or self._is_vip_or_admin(login_user):
            return

        for method in enabled_image_methods:
            if method in self._vip_only_image_methods:
                raise BusinessException(
                    ErrorCode.NO_AUTH_ERROR,
                    "高级配图功能（AI 生图、SVG 图表）仅限 VIP 会员使用",
                )

    def _to_blog_vo(self, blog) -> BlogVO:
        """转换为 BlogVO"""
        blog_dict = dict(blog)
        title_options = json.loads(blog_dict["titleOptions"]) if blog_dict.get("titleOptions") else None
        outline = json.loads(blog_dict["outline"]) if blog_dict.get("outline") else None
        images = json.loads(blog_dict["images"]) if blog_dict.get("images") else None
        return BlogVO(
            id=blog_dict["id"],
            taskId=blog_dict["taskId"],
            userId=blog_dict["userId"],
            topic=blog_dict["topic"],
            userDescription=blog_dict.get("userDescription"),
            style=blog_dict.get("style"),
            mainTitle=blog_dict.get("mainTitle"),
            subTitle=blog_dict.get("subTitle"),
            titleOptions=title_options,
            outline=outline,
            content=blog_dict.get("content"),
            fullContent=blog_dict.get("fullContent"),
            coverImage=blog_dict.get("coverImage"),
            images=images,
            status=blog_dict["status"],
            phase=blog_dict.get("phase"),
            errorMessage=blog_dict.get("errorMessage"),
            createTime=blog_dict["createTime"].isoformat(),
            completedTime=blog_dict["completedTime"].isoformat() if blog_dict.get("completedTime") else None,
            updateTime=blog_dict["updateTime"].isoformat(),
        )