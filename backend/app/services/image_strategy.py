"""图片服务策略选择器"""

import logging
from typing import Dict, List, Optional

from app.models.enums import ImageMethodEnum
from app.services.image_search import ImageSearchService
from app.services.image_pexels import ImagePexelsService
from app.services.image_mermaid import ImageMermaidService
from app.services.image_iconify import ImageIconifyService
from app.services.image_emoji import ImageEmojiService
from app.services.image_svg import ImageSvgService
from app.services.oss import OssService
from app.schemas.image import ImageRequest, ImageData
from app.constants.blog import BlogConstant

logger = logging.getLogger(__name__)


class ImageResult:
    """图片获取结果"""
    
    def __init__(self, url: str, method: ImageMethodEnum):
        self.url = url
        self.method = method
    
    def is_success(self) -> bool:
        """判断是否成功"""
        return self.url is not None and len(self.url) > 0


class ImageStrategy:
    """图片策略选择器"""
    
    def __init__(self):
        self.service_map: Dict[ImageMethodEnum, ImageSearchService] = {}
        self.oss_service = OssService()
        self._register_services()
    
    def _register_services(self):
        """注册所有图片服务"""
        services = [
            ImagePexelsService(), ImageMermaidService(),
            ImageIconifyService(), ImageEmojiService(), ImageSvgService(),
        ]
        for service in services:
            self.service_map[service.get_method()] = service
    
    async def get_image_and_upload(
        self,
        image_source: str,
        request: ImageRequest
    ) -> ImageResult:
        """获取图片并上传到 OSS（推荐使用的主方法）"""
        method = self._resolve_method(image_source)
        service = self.service_map.get(method)
        
        if service is None or not service.is_available():
            return await self._handle_fallback_with_upload(request.position)
        
        try:
            image_data = await service.get_image_data(request)
            
            if image_data is None or not image_data.is_valid():
                return await self._handle_fallback_with_upload(request.position)
            
            folder = self._get_folder_for_method(method)
            oss_url = await self.oss_service.upload_image_data(image_data, folder)
            
            if oss_url:
                return ImageResult(oss_url, method)
            else:
                return await self._handle_fallback_with_upload(request.position)
        except Exception as e:
            logger.error(f"获取图片并上传异常, method={method}, error={e}")
            return await self._handle_fallback_with_upload(request.position)
    
    async def _handle_fallback_with_upload(self, position: Optional[int]) -> ImageResult:
        """处理降级逻辑（降级图片也上传到 OSS）"""
        pos = position if position else 1
        fallback_url = BlogConstant.PICSUM_URL_TEMPLATE.format(pos)
        fallback_data = ImageData.from_url(fallback_url)
        oss_url = await self.oss_service.upload_image_data(fallback_data, "fallback")
        final_url = oss_url if oss_url else fallback_url
        return ImageResult(final_url, ImageMethodEnum.get_fallback_method())
