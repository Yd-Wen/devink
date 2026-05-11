"""Pexels 图片检索服务"""

import httpx
import logging
from typing import Optional
from urllib.parse import quote

from app.config import settings
from app.constants.blog import BlogConstant
from app.models.enums import ImageMethodEnum
from app.services.image_search import ImageSearchService

logger = logging.getLogger(__name__)


class ImagePexelsService(ImageSearchService):
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
                logger.error(f"Pexels API 返回非 200 状态码: {response.status_code}, body={response.text[:200]}, keywords={keywords}")
                return None
            
            return self._extract_image_url(response.json(), keywords)
        except Exception as e:
            logger.error(f"Pexels API 调用异常: {repr(e)}, keywords={keywords}")
            return None
    
    def get_method(self) -> ImageMethodEnum:
        """获取配图方式"""
        return ImageMethodEnum.PEXELS

    def get_fallback_image(self, position: int) -> str:
        """获取降级图片"""
        return BlogConstant.PICSUM_URL_TEMPLATE.format(position)
    
    def _build_search_url(self, keywords: str) -> str:
        """构建搜索 URL"""
        return (
            f"{BlogConstant.PEXELS_API_URL}"
            f"?query={quote(keywords)}"
            f"&per_page={BlogConstant.PEXELS_PER_PAGE}"
            f"&orientation={BlogConstant.PEXELS_ORIENTATION_LANDSCAPE}"
        )
    
    def _extract_image_url(self, response_data: dict, keywords: str) -> Optional[str]:
        """从响应中提取图片 URL"""
        photos = response_data.get("photos", [])
        if not photos:
            total_results = response_data.get("total_results", 0)
            logger.warning(f"Pexels API 未找到图片: keywords={keywords}, total_results={total_results}")
            return None

        photo = photos[0]
        src = photo.get("src", {})
        image_url = src.get("large")
        if not image_url:
            logger.warning(f"Pexels API 响应中缺少图片 URL: keywords={keywords}, src_keys={list(src.keys())}")
        return image_url
