"""配图需求分析智能体适配器"""

from app.schemas.blog import BlogState


class ImageAnalyzerAgent:
    """配图需求分析智能体"""

    async def run(self, service, state: BlogState):
        await service.img_req_agent_analyze_image_requirements(state)
