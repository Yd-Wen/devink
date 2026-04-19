"""API 路由"""

from app.routers.user import router as user_router
from app.routers.health import router as health_router
from app.routers.blog import router as blog_router
from app.routers.statistics import router as statistics_router

__all__ = [
    "user_router",
    "health_router",
    "blog_router",
    "statistics_router",
]