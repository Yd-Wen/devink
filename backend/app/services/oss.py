"""阿里云 OSS 服务"""

import logging
import httpx
import uuid
from typing import Optional
from qcloud_cos import CosConfig, CosS3Client
import alibabacloud_oss_v2 as oss
from io import BytesIO

from app.config import settings
from app.schemas.image import ImageData, DataType

logger = logging.getLogger(__name__)


class OssService:
    """阿里云 OSS 服务"""
    
    def __init__(self):
        # 加载凭证信息，用于身份验证
        credentials_provider = oss.credentials.StaticCredentialsProvider(
            access_key_id=settings.alicloud_oss_secret_id,
            access_key_secret=settings.alicloud_oss_secret_key
        )

        # 加载SDK的默认配置，并设置凭证提供者
        cfg = oss.config.load_default()
        cfg.credentials_provider = credentials_provider

        # Bucket所在地域
        cfg.region = settings.alicloud_oss_region

        # 自定义域名。例如www.example-***.com
        cfg.endpoint = settings.alicloud_oss_domain

        # 请注意，设置true开启CNAME选项，否则无法使用自定义域名
        cfg.use_cname = True

        # 使用配置好的信息创建OSS客户端
        self.bucket = settings.alicloud_oss_bucket
        self.endpoint = settings.alicloud_oss_domain
        self.client = oss.Client(cfg)
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def upload_image(self, image_url: str, folder: str) -> str:
        """
        上传图片到 OSS
        
        Args:
            image_url: 图片 URL
            folder: 文件夹
            
        Returns:
            OSS 图片 URL
        """
        try:
            # 下载图片
            response = await self.http_client.get(image_url)
            if response.status_code != 200:
                logger.error(f"下载图片失败: {image_url}")
                return image_url  # 降级：直接返回原始 URL
            
            image_bytes = response.content
            
            # 生成文件名
            import uuid
            file_name = f"{folder}/{uuid.uuid4()}.jpg"
            
            # 上传到 OSS
            self.client.put_object(oss.PutObjectRequest(
                bucket=self.bucket,
                key=file_name,
                body=BytesIO(image_bytes),
                content_type='image/jpeg'
            ))
            
            # 返回访问 URL
            return f"{self.endpoint}/{file_name}"
        except Exception as e:
            logger.error(f"上传图片到 OSS 失败: {e}")
            return image_url  # 降级：直接返回原始 URL
    
    async def upload_image_data(
        self,
        image_data: ImageData,
        folder: str
    ) -> Optional[str]:
        """
        上传图片数据到 OSS（第 5 期新增）
        支持多种数据格式：字节数据、URL、data URL
        
        Args:
            image_data: 图片数据
            folder: 文件夹
            
        Returns:
            OSS 图片 URL
        """
        if not image_data or not image_data.is_valid():
            logger.warning("图片数据无效")
            return None
        
        try:
            # 1. 获取图片字节数据
            if image_data.data_type == DataType.BYTES:
                image_bytes = image_data.bytes
            elif image_data.data_type == DataType.DATA_URL:
                image_bytes = image_data.get_image_bytes()
            elif image_data.data_type == DataType.URL:
                # 下载图片
                response = await self.http_client.get(image_data.url)
                if response.status_code != 200:
                    logger.error(f"下载图片失败: {image_data.url}")
                    return image_data.url  # 降级：直接返回原始 URL
                image_bytes = response.content
            else:
                logger.error(f"未知的数据类型: {image_data.data_type}")
                return None
            
            if not image_bytes:
                logger.error("图片字节数据为空")
                return None
            
            # 2. 生成文件名
            extension = image_data.get_file_extension()
            file_name = f"{folder}/{uuid.uuid4()}{extension}"
            
            # 3. 上传到 OSS
            self.client.put_object(oss.PutObjectRequest(
                bucket=self.bucket,
                body=BytesIO(image_bytes),
                key=file_name,
                content_type=image_data.mime_type
            ))
            
            # 4. 返回访问 URL
            cos_url = f"{self.endpoint}/{file_name}"
            logger.info(f"图片上传成功, size={len(image_bytes)} bytes, cosUrl={cos_url}")
            
            return cos_url
        except Exception as e:
            logger.error(f"上传图片数据到 OSS 失败: {e}")
            # 如果是 URL 类型，降级返回原始 URL
            if image_data.data_type == DataType.URL:
                return image_data.url
            return None
    
    def use_direct_url(self, image_url: str) -> str:
        """
        直接使用图片 URL（不上传到 OSS）
        
        Args:
            image_url: 图片 URL
            
        Returns:
            图片 URL
        """
        return image_url
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.http_client.aclose()
