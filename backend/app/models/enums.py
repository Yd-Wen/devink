"""枚举类型定义"""

from enum import Enum


class ArticleStatusEnum(str, Enum):
    """博客状态枚举"""
    
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ImageMethodEnum(str, Enum):
    """配图方式枚举"""
    
    PEXELS = "PEXELS"
    PICSUM = "PICSUM"


class SseMessageTypeEnum(str, Enum):
    """SSE 消息类型枚举"""
    
    TITLE_AGENT_COMPLETE = "TITLE_AGENT_COMPLETE"    # 标题智能体完成（生成标题）
    OUTLINE_AGENT_STREAMING = "OUTLINE_AGENT_STREAMING"  # 大纲智能体流式输出（大纲）
    OUTLINE_AGENT_COMPLETE = "OUTLINE_AGENT_COMPLETE"    # 大纲智能体完成
    CONTENT_AGENT_STREAMING = "CONTENT_AGENT_STREAMING"  # 正文智能体流式输出（正文）
    CONTENT_AGENT_COMPLETE = "CONTENT_AGENT_COMPLETE"    # 正文智能体完成
    IMG_REQ_AGENT_COMPLETE = "IMAGE_REQ_AGENT_COMPLETE"    # 配图分析智能体完成（配图需求）
    IMAGE_COMPLETE = "IMAGE_COMPLETE"      # 单张配图完成
    IMG_RES_AGENT_COMPLETE = "IMG_RES_AGENT_COMPLETE"    # 配图生成智能体完成（配图结果）
    MERGE_COMPLETE = "MERGE_COMPLETE"      # 图文合成完成
    ALL_COMPLETE = "ALL_COMPLETE"          # 全部完成
    ERROR = "ERROR"                        # 错误
    
    def get_streaming_prefix(self) -> str:
        """获取流式输出消息前缀"""
        return f"{self.value}:"
