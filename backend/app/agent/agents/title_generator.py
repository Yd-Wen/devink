"""标题生成智能体适配器"""

from app.schemas.blog import BlogState


class TitleGeneratorAgent:
    """标题生成智能体"""

    async def run(self, service, state: BlogState):
        await service.title_agent_generate_title_options(state)
