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
