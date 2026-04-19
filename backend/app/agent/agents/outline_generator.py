"""大纲生成智能体适配器"""

from app.schemas.blog import BlogState


class OutlineGeneratorAgent:
    """大纲生成智能体"""

    async def run(self, service, state: BlogState, stream_handler):
        await service.outline_agent_generate_outline(state, stream_handler)
