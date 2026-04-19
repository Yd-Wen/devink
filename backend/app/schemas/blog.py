"""博客相关请求/响应模型"""

from typing import Optional, List
from pydantic import BaseModel, Field

from app.schemas.common import PageRequest


class TitleResult(BaseModel):
    """标题结果"""
    
    main_title: str = Field(..., alias="mainTitle")
    sub_title: str = Field(..., alias="subTitle")
    
    class Config:
        populate_by_name = True


class OutlineSection(BaseModel):
    """大纲章节"""
    
    section: int
    title: str
    points: List[str]


class OutlineResult(BaseModel):
    """大纲结果"""
    
    sections: List[OutlineSection]


class ImageRequirement(BaseModel):
    """配图需求"""
    
    position: int
    type: str
    section_title: str = Field(..., alias="sectionTitle")
    keywords: str
    image_source: str = Field(..., alias="imageSource", description="图片来源")
    prompt: str = Field(default="", description="AI 生图提示词")
    placeholder_id: str = Field(..., alias="placeholderId", description="占位符ID")
    
    class Config:
        populate_by_name = True


class ImgReqAgentResult(BaseModel):
    """配图分析智能体返回结果（第 5 期：占位符方案）"""
    
    content_with_placeholders: str = Field(..., alias="contentWithPlaceholders")
    image_requirements: List[ImageRequirement] = Field(..., alias="imageRequirements")
    
    class Config:
        populate_by_name = True


class ImageResult(BaseModel):
    """配图结果"""
    
    position: int
    url: str
    method: str
    keywords: str
    section_title: str = Field(..., alias="sectionTitle")
    description: str
    
    class Config:
        populate_by_name = True


class BlogState:
    """博客生成状态（智能体间共享的状态对象）"""
    
    def __init__(self):
        self.task_id: Optional[str] = None
        self.topic: Optional[str] = None
        self.title: Optional[TitleResult] = None
        self.outline: Optional[OutlineResult] = None
        self.content: Optional[str] = None
        self.image_requirements: Optional[List[ImageRequirement]] = None
        self.images: Optional[List[ImageResult]] = None
        self.cover_image: Optional[str] = None
        self.full_content: Optional[str] = None


class BlogCreateRequest(BaseModel):
    """创建文章请求"""
    
    topic: str = Field(..., min_length=1, description="选题")
    style: Optional[str] = Field(None, description="博客风格：tech/emotional/educational/humorous")
    enabled_image_methods: Optional[List[str]] = Field(
        None, alias="enabledImageMethods",
        description="允许的配图方式列表（为空表示支持所有方式）"
    )
