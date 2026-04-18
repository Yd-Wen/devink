"""智能体编排服务"""

import json
import logging
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime
from typing import Callable, List, Optional
from openai import AsyncOpenAI

# from app.agent.orchestrator import ArticleAgentOrchestrator
# from app.agent.parallel.image_generator import ParallelImageGenerator
from app.config import settings
from app.constants.prompt import PromptConstant
from app.database import database
from app.schemas.blog import (
    TitleOption,
    BlogState,
    OutlineResult,
    OutlineSection,
    ImageRequirement,
    ImageResult,
    Agent4Result
)
from app.models.enums import SseMessageTypeEnum
from app.services.agent_log import AgentLogService
from app.services.image_strategy import ImageStrategy

logger = logging.getLogger(__name__)


class AgentService:
    """智能体编排服务"""
    
    def __init__(self):
        # 初始化 OpenAI 客户端（DashScope 兼容）
        self.client = AsyncOpenAI(
            api_key=settings.dashscope_api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.model = settings.dashscope_model
        
        # 初始化服务
        self.pexels_service = PexelsService()
        self.oss_service = OssService()

    async def _completions(self, prompt: str) -> str:
        """调用 LLM（非流式）"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    async def _stream(
        self,
        prompt: str,
        stream_handler: Callable[[str], None],
        message_type: SseMessageTypeEnum
    ) -> str:
        """调用 LLM（流式输出）"""
        content_builder = []
        
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                content_builder.append(content)
                stream_handler(message_type.get_streaming_prefix() + content)
        
        return "".join(content_builder)
    
    def _parse_json_response(self, content: str, name: str) -> dict:
        """解析 JSON 响应"""
        try:
            result = json.loads(content)
            if not isinstance(result, dict):
                raise ValueError("响应不是 JSON 对象")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"{name}解析失败, content={content}, error={e}")
            raise RuntimeError(f"{name}解析失败")
        except ValueError as e:
            logger.error(f"{name}解析失败, content={content}, error={e}")
            raise RuntimeError(f"{name}解析失败")

    def _parse_json_list_response(self, content: str, name: str) -> list:
        """解析 JSON 数组响应"""
        try:
            result = json.loads(content)
            if not isinstance(result, list):
                raise ValueError("响应不是 JSON 数组")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"{name}解析失败, content={content}, error={e}")
            raise RuntimeError(f"{name}解析失败")
        except ValueError as e:
            logger.error(f"{name}解析失败, content={content}, error={e}")
            raise RuntimeError(f"{name}解析失败")
    
    async def execute_blog_generation(
        self,
        state: BlogState,
        stream_handler: Callable[[str], None]
    ):
        """执行完整的文章生成流程"""
        try:
            # 智能体1：生成标题
            await self.generate_title(state)
            stream_handler(SseMessageTypeEnum.TITLE_AGENT_COMPLETE.value)
            
            # 智能体2：生成大纲（流式输出）
            await self.generate_outline(state, stream_handler)
            stream_handler(SseMessageTypeEnum.OUTLINE_AGENT_COMPLETE.value)
            
            # 智能体3：生成正文（流式输出）
            await self.generate_content(state, stream_handler)
            stream_handler(SseMessageTypeEnum.CONTENT_AGENT_COMPLETE.value)
            
            # 智能体4：分析配图需求
            await self.analyze_image_requirements(state)
            stream_handler(SseMessageTypeEnum.IMAGE_REQ_AGENT_COMPLETE.value)
            
            # 智能体5：生成配图
            await self.generate_images(state, stream_handler)
            stream_handler(SseMessageTypeEnum.IMG_RES_AGENT_COMPLETE.value)
            
            # 图文合成：将配图插入正文
            self.merge_images_into_content(state)
            stream_handler(SseMessageTypeEnum.MERGE_COMPLETE.value)
        except Exception as e:
            raise RuntimeError(f"文章生成失败: {str(e)}")

    async def generate_title(self, state: BlogState):
        """标题智能体：生成标题"""
        prompt = PromptConstant.TITLE_AGENT_PROMPT.replace("{topic}", state.topic)
        
        content = await self._completions(prompt)
        title_data = self._parse_json_response(content, "标题")
        state.title = TitleResult(**title_data)

    async def generate_outline(
        self,
        state: BlogState,
        stream_handler: Callable[[str], None]
    ):
        """大纲智能体：生成大纲（流式输出）"""
        prompt = (
            PromptConstant.OUTLINE_AGENT_PROMPT
            .replace("{mainTitle}", state.title.main_title)
            .replace("{subTitle}", state.title.sub_title)
        )
        
        content = await self._stream(
            prompt, stream_handler, SseMessageTypeEnum.OUTLINE_AGENT_STREAMING
        )
        outline_data = self._parse_json_response(content, "大纲")
        sections = [OutlineSection(**section) for section in outline_data["sections"]]
        state.outline = OutlineResult(sections=sections)

    async def generate_content(
        self,
        state: BlogState,
        stream_handler: Callable[[str], None]
    ):
        """正文智能体：生成正文（流式输出）"""
        outline_text = json.dumps(
            [section.model_dump() for section in state.outline.sections],
            ensure_ascii=False
        )
        prompt = (
            PromptConstant.CONTENT_AGENT_PROMPT
            .replace("{mainTitle}", state.title.main_title)
            .replace("{subTitle}", state.title.sub_title)
            .replace("{outline}", outline_text)
        )
        
        content = await self._stream(
            prompt, stream_handler, SseMessageTypeEnum.CONTENT_AGENT_STREAMING
        )
        state.content = content

    async def analyze_image_requirements(self, state: BlogState):
        """配图需求智能体：分析配图需求"""
        prompt = (
            PromptConstant.IMAGE_REQ_AGENT_COMPLETE
            .replace("{mainTitle}", state.title.main_title)
            .replace("{content}", state.content)
        )
        
        content = await self._completions(prompt)
        requirements_data = self._parse_json_response(content, "配图需求", is_list=True)
        state.image_requirements = [ImageRequirement(**req) for req in requirements_data]

    async def generate_images(
        self,
        state: BlogState,
        stream_handler: Callable[[str], None]
    ):
        """智能体5：生成配图（串行执行）"""
        image_results = []
        
        for requirement in state.image_requirements:
            # 调用图片检索服务
            image_url = await self.pexels_service.search_image(requirement.keywords)
            
            # 降级策略：Pexels 失败时使用 Picsum 随机图片兜底
            method = self.pexels_service.get_method()
            if image_url is None:
                image_url = self.pexels_service.get_fallback_image(requirement.position)
                method = ImageMethodEnum.PICSUM
            
            # MVP 阶段直接使用图片 URL，不上传到 COS
            final_image_url = self.oss_service.use_direct_url(image_url)
            
            # 创建配图结果
            image_result = self._build_image_result(requirement, final_image_url, method)
            image_results.append(image_result)
            
            # 推送单张配图完成
            image_complete_message = (
                SseMessageTypeEnum.IMAGE_COMPLETE.get_streaming_prefix() +
                image_result.model_dump_json(by_alias=True)
            )
            stream_handler(image_complete_message)
        
        state.images = image_results

    def merge_images2content(self, state: BlogState):
        """图文合成：将配图插入正文对应位置"""
        content = state.content
        images = state.images
        
        if not images:
            state.full_content = content
            return
        
        full_content_lines = []
        
        # 按行处理正文，在章节标题后插入对应图片
        lines = content.split("\n")
        for line in lines:
            full_content_lines.append(line)
            
            if line.startswith("## "):
                section_title = line[3:].strip()
                self._insert_image_after_section(full_content_lines, images, section_title)
        
        state.full_content = "\n".join(full_content_lines)


