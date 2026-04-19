from abc import ABC, abstractmethod
from typing import Optional

from app.models.enums import ImageMethodEnum
from app.schemas.image import ImageRequest, ImageData


class ImageSearchService(ABC):
    """图片服务接口，抽象图片获取逻辑，便于扩展多种图片来源"""
    
    async def get_image(self, request: ImageRequest) -> Optional[str]:
        """根据请求获取图片（默认实现，子类可重写）"""
        param = request.get_effective_param(self.get_method().is_ai_generated())
        return await self.search_image(param)
    
    async def get_image_data(self, request: ImageRequest) -> Optional[ImageData]:
        """获取图片数据，用于统一上传到 COS（子类可重写）"""
        url = await self.get_image(request)
        return ImageData.from_url(url)
    
    @abstractmethod
    async def search_image(self, keywords: str) -> Optional[str]:
        """根据关键词/提示词获取图片"""
        pass
    
    @abstractmethod
    def get_method(self) -> ImageMethodEnum:
        """获取图片服务类型"""
        pass
    
    @abstractmethod
    def get_fallback_image(self, position: int) -> str:
        """获取降级图片 URL"""
        pass
    
    def is_available(self) -> bool:
        """判断服务是否可用（子类可重写进行健康检查）"""
        return True
