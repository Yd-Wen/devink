"""正文生成智能体适配器"""

from app.schemas.blog import BlogState


class ContentGeneratorAgent:
    """正文生成智能体"""

    async def run(self, service, state: BlogState, stream_handler):
        await service.content_agent_generate_content(state, stream_handler)
