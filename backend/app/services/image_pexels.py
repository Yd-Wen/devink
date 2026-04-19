"""Pexels 图片检索服务"""

import httpx
import logging
from typing import Optional

from app.config import settings
from app.constants.blog import BlogConstant
from app.models.enums import ImageMethodEnum
from app.services.image_search import ImageSearchService

logger = logging.getLogger(__name__)


class ImagePexelsService:
    """Pexels 图片检索服务"""
    
    def __init__(self):
        self.api_key = settings.pexels_api_key
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_image(self, keywords: str) -> Optional[str]:
        """根据关键词搜索图片"""
        try:
            url = self._build_search_url(keywords)
            headers = {"Authorization": self.api_key}
            response = await self.client.get(url, headers=headers)
            
            if response.status_code != 200:
                return None
            
            return self._extract_image_url(response.json(), keywords)
        except Exception as e:
            logger.error(f"Pexels API 调用异常: {e}")
            return None
    
    def _build_search_url(self, keywords: str) -> str:
        """构建搜索 URL"""
        return (
            f"{BlogConstant.PEXELS_API_URL}"
            f"?query={keywords}"
            f"&per_page={BlogConstant.PEXELS_PER_PAGE}"
            f"&orientation={BlogConstant.PEXELS_ORIENTATION_LANDSCAPE}"
        )
    
    def _extract_image_url(self, response_data: dict, keywords: str) -> Optional[str]:
        """从响应中提取图片 URL"""
        photos = response_data.get("photos", [])
        if not photos:
            return None
        
        photo = photos[0]
        src = photo.get("src", {})
        return src.get("large")
