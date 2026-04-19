"""图文合并智能体适配器"""

from app.schemas.blog import BlogState


class MergerAgent:
    """图文合并智能体"""

    def run(self, service, state: BlogState):
        service.merge_images_into_content(state)
