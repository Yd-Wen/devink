"""图片相关数据模型"""

import base64
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


class ImageRequest(BaseModel):
    """图片请求对象"""
    
    keywords: Optional[str] = Field(None, description="搜索关键词（用于图库检索）")
    prompt: Optional[str] = Field(None, description="生图提示词（用于 AI 生图）")
    position: Optional[int] = Field(None, description="图片位置序号")
    type: Optional[str] = Field(None, description="图片类型（cover/section）")
    aspect_ratio: Optional[str] = Field(None, description="宽高比（如 16:9, 1:1）")
    style: Optional[str] = Field(None, description="图片风格描述")
    
    def get_effective_param(self, is_ai_generated: bool) -> str:
        """AI 生图优先使用 prompt，图库检索使用 keywords"""
        if is_ai_generated:
            return self.prompt if self.prompt else self.keywords or ""
        return self.keywords if self.keywords else self.prompt or ""


class DataType(str, Enum):
    BYTES = "BYTES"       # 字节数据（Mermaid、Nano Banana 等）
    URL = "URL"           # 外部 URL（Pexels、Iconify 等）
    DATA_URL = "DATA_URL" # base64 data URL


class ImageData:
    """图片数据封装类"""
    
    def __init__(
        self,
        bytes_data: Optional[bytes] = None,
        url: Optional[str] = None,
        mime_type: Optional[str] = None,
        data_type: Optional[DataType] = None
    ):
        self.bytes = bytes_data
        self.url = url
        self.mime_type = mime_type or "image/png"
        self.data_type = data_type
    
    @classmethod
    def from_url(cls, url: Optional[str]) -> Optional["ImageData"]:
        if not url:
            return None
        if url.startswith("data:"):
            return cls.from_data_url(url)
        return cls(url=url, data_type=DataType.URL)
    
    @classmethod
    def from_bytes(cls, bytes_data: bytes, mime_type: str = "image/png") -> Optional["ImageData"]:
        if not bytes_data:
            return None
        return cls(bytes_data=bytes_data, mime_type=mime_type, data_type=DataType.BYTES)
    
    def is_valid(self) -> bool:
        if self.data_type == DataType.BYTES:
            return self.bytes is not None and len(self.bytes) > 0
        elif self.data_type in [DataType.URL, DataType.DATA_URL]:
            return self.url is not None and len(self.url) > 0
        return False
    
    def get_file_extension(self) -> str:
        if not self.mime_type:
            return ".png"
        mime_lower = self.mime_type.lower()
        if mime_lower in ["image/jpeg", "image/jpg"]:
            return ".jpg"
        elif mime_lower == "image/svg+xml":
            return ".svg"
        return ".png"
