"""文章异步任务服务"""

import json
import logging
from typing import Any, Dict, Optional

from app.schemas.blog import BlogState, OutlineSection, OutlineResult, TitleResult
from app.models.enums import BlogPhaseEnum, BlogStatusEnum, SseMessageTypeEnum
from app.services.blog_agent import BlogAgentService
from app.services.blog import BlogService
from app.managers.sse import sse_emitter_manager
from app.database import database

logger = logging.getLogger(__name__)


class BlogAsyncService:
    """博客异步任务服务"""

    async def execute_phase1(
        self,
        task_id: str,
        topic: str,
        style: Optional[str] = None,
    ):
        """阶段1：异步生成标题方案"""
        logger.info("阶段1异步任务开始, taskId=%s, topic=%s, style=%s", task_id, topic, style)
        blog_agent_service = BlogAgentService()
        blog_service = BlogService(database)

        try:
            await blog_service.update_blog_status(task_id, BlogStatusEnum.PROCESSING)
            await blog_service.update_phase(task_id, BlogPhaseEnum.TITLE_GENERATING)

            state = BlogState()
            state.task_id = task_id
            state.topic = topic
            state.style = style

            await blog_agent_service.execute_phase1_generate_titles(
                state,
                lambda message: self._handle_agent_message(task_id, message, state)
            )

            await blog_service.save_title_options(task_id, state.title_options or [])
            await blog_service.update_phase(task_id, BlogPhaseEnum.TITLE_SELECTING)

            self._send_sse_message(
                task_id,
                SseMessageTypeEnum.TITLES_GENERATED,
                {
                    "titleOptions": [
                        item.model_dump(by_alias=True) for item in (state.title_options or [])
                    ]
                },
            )

            logger.info("阶段1异步任务完成, taskId=%s", task_id)
        except Exception as e:
            logger.error("阶段1异步任务失败, taskId=%s, error=%s", task_id, e)
            await blog_service.update_blog_status(
                task_id,
                BlogStatusEnum.FAILED,
                str(e)
            )
            self._send_sse_message(
                task_id,
                SseMessageTypeEnum.ERROR,
                {"message": str(e)}
            )
            sse_emitter_manager.complete(task_id)

    async def execute_phase2(self, task_id: str):
        """阶段2：异步生成大纲"""
        logger.info("阶段2异步任务开始, taskId=%s", task_id)
        blog_agent_service = BlogAgentService()
        blog_service = BlogService(database)

        try:
            blog = await blog_service.get_by_task_id(task_id)
            if not blog:
                raise RuntimeError("文章不存在")

            state = BlogState()
            state.task_id = task_id
            state.style = blog["style"]
            state.user_description = blog["userDescription"]
            state.title = TitleResult(
                mainTitle=blog["mainTitle"],
                subTitle=blog["subTitle"],
            )

            await blog_agent_service.execute_phase2_generate_outline(
                state,
                lambda message: self._handle_agent_message(task_id, message, state)
            )
            await blog_service.save_outline(task_id, state.outline.sections if state.outline else [])
            await blog_service.update_phase(task_id, BlogPhaseEnum.OUTLINE_EDITING)

            self._send_sse_message(
                task_id,
                SseMessageTypeEnum.OUTLINE_GENERATED,
                {
                    "outline": [
                        item.model_dump() for item in (state.outline.sections if state.outline else [])
                    ]
                },
            )
            logger.info("阶段2异步任务完成, taskId=%s", task_id)
        except Exception as e:
            logger.error("阶段2异步任务失败, taskId=%s, error=%s", task_id, e)
            await blog_service.update_blog_status(task_id, BlogStatusEnum.FAILED, str(e))
            self._send_sse_message(task_id, SseMessageTypeEnum.ERROR, {"message": str(e)})
            sse_emitter_manager.complete(task_id)

    async def execute_phase3(self, task_id: str):
        """阶段3：异步生成正文与配图"""
        logger.info("阶段3异步任务开始, taskId=%s", task_id)
        blog_agent_service = BlogAgentService()
        blog_service = BlogService(database)

        try:
            blog = await blog_service.get_by_task_id(task_id)
            if not blog:
                raise RuntimeError("文章不存在")

            outline_data = json.loads(blog["outline"]) if blog["outline"] else []
            state = BlogState()
            state.task_id = task_id
            state.style = blog["style"]
            state.enabled_image_methods = (
                json.loads(blog["enabledImageMethods"])
                if blog["enabledImageMethods"]
                else None
            )
            state.title = TitleResult(
                mainTitle=blog["mainTitle"],
                subTitle=blog["subTitle"],
            )
            state.outline = OutlineResult(
                sections=[OutlineSection(**item) for item in outline_data]
            )

            await blog_agent_service.execute_phase3_generate_content(
                state,
                lambda message: self._handle_agent_message(task_id, message, state)
            )
            await blog_service.save_blog_content(task_id, state)
            await blog_service.update_blog_status(task_id, BlogStatusEnum.COMPLETED)
            remaining_quota = await blog_service.decrement_quota_on_completion(task_id)

            all_complete_data: Dict[str, Any] = {"taskId": task_id}
            if remaining_quota is not None:
                all_complete_data["remainingQuota"] = remaining_quota

            self._send_sse_message(
                task_id,
                SseMessageTypeEnum.ALL_COMPLETE,
                all_complete_data
            )
            sse_emitter_manager.complete(task_id)
            logger.info("阶段3异步任务完成, taskId=%s", task_id)
        except Exception as e:
            logger.error("阶段3异步任务失败, taskId=%s, error=%s", task_id, e)
            await blog_service.update_blog_status(task_id, BlogStatusEnum.FAILED, str(e))
            self._send_sse_message(task_id, SseMessageTypeEnum.ERROR, {"message": str(e)})
            sse_emitter_manager.complete(task_id)

    def _handle_agent_message(self, task_id: str, message: str, state: BlogState):
        """处理智能体消息并推送"""
        data = self._build_message_data(message, state)
        if data is not None:
            sse_emitter_manager.send(task_id, json.dumps(data, ensure_ascii=False))
    
    def _build_message_data(self, message: str, state: BlogState) -> Dict[str, Any]:
        """构建消息数据"""
        # 处理流式消息（带冒号分隔符）
        outline_streaming_prefix = SseMessageTypeEnum.OUTLINE_AGENT_STREAMING.get_streaming_prefix()
        content_streaming_prefix = SseMessageTypeEnum.CONTENT_AGENT_STREAMING.get_streaming_prefix()
        image_complete_prefix = SseMessageTypeEnum.IMAGE_COMPLETE.get_streaming_prefix()
        
        if message.startswith(outline_streaming_prefix):
            return self._build_streaming_data(
                SseMessageTypeEnum.OUTLINE_AGENT_STREAMING,
                message[len(outline_streaming_prefix):]
            )
        
        if message.startswith(content_streaming_prefix):
            return self._build_streaming_data(
                SseMessageTypeEnum.CONTENT_AGENT_STREAMING,
                message[len(content_streaming_prefix):]
            )
        
        if message.startswith(image_complete_prefix):
            image_json = message[len(image_complete_prefix):]
            return self._build_image_complete_data(image_json)
        
        # 处理完成消息（枚举值）
        return self._build_complete_message_data(message, state)
    
    def _build_streaming_data(self, type_enum: SseMessageTypeEnum, content: str) -> Dict[str, Any]:
        """构建流式输出数据"""
        return {
            "type": type_enum.value,
            "content": content
        }
    
    def _build_image_complete_data(self, image_json: str) -> Dict[str, Any]:
        """构建图片完成数据"""
        return {
            "type": SseMessageTypeEnum.IMAGE_COMPLETE.value,
            "image": json.loads(image_json)
        }
    
    def _build_complete_message_data(self, message: str, state: BlogState) -> Dict[str, Any]:
        """构建完成消息数据"""
        data = {}
        
        if message == SseMessageTypeEnum.TITLE_AGENT_COMPLETE.value:
            data["type"] = SseMessageTypeEnum.TITLE_AGENT_COMPLETE.value
            data["titleOptions"] = [
                item.model_dump(by_alias=True) for item in (state.title_options or [])
            ]
        elif message == SseMessageTypeEnum.OUTLINE_AGENT_COMPLETE.value:
            data["type"] = SseMessageTypeEnum.OUTLINE_AGENT_COMPLETE.value
            data["outline"] = [s.model_dump() for s in state.outline.sections] if state.outline else []
        elif message == SseMessageTypeEnum.CONTENT_AGENT_COMPLETE.value:
            data["type"] = SseMessageTypeEnum.CONTENT_AGENT_COMPLETE.value
        elif message == SseMessageTypeEnum.IMAGE_REQ_AGENT_COMPLETE.value:
            data["type"] = SseMessageTypeEnum.IMAGE_REQ_AGENT_COMPLETE.value
            data["imageRequirements"] = [
                req.model_dump(by_alias=True) for req in state.image_requirements
            ] if state.image_requirements else []
        elif message == SseMessageTypeEnum.IMAGE_RES_AGENT_COMPLETE.value:
            data["type"] = SseMessageTypeEnum.IMAGE_RES_AGENT_COMPLETE.value
            data["images"] = [
                img.model_dump(by_alias=True) for img in state.images
            ] if state.images else []
        elif message == SseMessageTypeEnum.MERGE_COMPLETE.value:
            data["type"] = SseMessageTypeEnum.MERGE_COMPLETE.value
            data["fullContent"] = state.full_content
        else:
            return None
        
        return data
    
    def _send_sse_message(
        self,
        task_id: str,
        type_enum: SseMessageTypeEnum,
        additional_data: Dict[str, Any]
    ):
        """发送 SSE 消息"""
        data = {"type": type_enum.value}
        data.update(additional_data)
        sse_emitter_manager.send(task_id, json.dumps(data, ensure_ascii=False))


# 全局单例
blog_async_service = BlogAsyncService()
