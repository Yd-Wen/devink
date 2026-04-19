class ImageIconifyService(ImageSearchService):
    """Iconify 图标库检索服务"""
    
    async def search_image(self, keywords: str) -> Optional[str]:
        """搜索图标并返回 SVG URL"""
        try:
            search_url = f"{self.api_url}/search?query={quote(keywords)}&limit={self.search_limit}"
            response = await self.client.get(search_url)
            if response.status_code != 200:
                return None
            
            icons = response.json().get("icons", [])
            if not icons:
                return None
            
            # 将 "mdi:home" 格式转换为 URL 路径 "mdi/home"
            icon_name = icons[0]
            path = icon_name.replace(":", "/")
            url = f"{self.api_url}/{path}.svg"
            
            # 添加高度和颜色参数
            params = []
            if self.default_height > 0:
                params.append(f"height={self.default_height}")
            if self.default_color:
                color = self.default_color
                if color.startswith("#"):
                    color = "%23" + color[1:]
                params.append(f"color={color}")
            
            if params:
                url += "?" + "&".join(params)
            
            return url
        except Exception as e:
            logger.error(f"Iconify 图标检索异常, keywords={keywords}, error={e}")
            return None
    
    def get_method(self) -> ImageMethodEnum:
        return ImageMethodEnum.ICONIFY
    
    def get_fallback_image(self, position: int) -> str:
        return ArticleConstant.PICSUM_URL_TEMPLATE.format(position)
