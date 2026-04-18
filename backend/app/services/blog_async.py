class BlogAsyncService:
    """文章异步任务服务"""
    
    async def execute_blog_generation(self, task_id: str, topic: str):
        """异步执行文章生成"""
        blog_agent_service = BlogAgentService()
        blog_service = BlogService(database)
        
        try:
            # 更新状态为处理中
            await blog_service.update_blog_status(task_id, BlogStatusEnum.PROCESSING)
            
            # 创建状态对象
            state = BlogState()
            state.task_id = task_id
            state.topic = topic
            
            # 执行智能体编排，通过 SSE 推送进度
            await blog_agent_service.execute_blog_generation(
                state,
                lambda message: self._handle_agent_message(task_id, message, state)
            )
            
            # 保存完整文章到数据库
            await blog_service.save_blog_content(task_id, state)
            
            # 更新状态为已完成
            await blog_service.update_blog_status(task_id, BlogStatusEnum.COMPLETED)
            
            # 推送完成消息并关闭 SSE 连接
            self._send_sse_message(task_id, SseMessageTypeEnum.ALL_COMPLETE, {"taskId": task_id})
            sse_emitter_manager.complete(task_id)
        except Exception as e:
            logger.error(f"异步任务失败, taskId={task_id}, error={e}")
            
            await blog_service.update_blog_status(task_id, BlogStatusEnum.FAILED, str(e))
            self._send_sse_message(task_id, SseMessageTypeEnum.ERROR, {"message": str(e)})
            sse_emitter_manager.complete(task_id)

    def _build_message_data(self, message: str, state: BlogState) -> Dict[str, Any]:
        """构建消息数据"""
        streaming_prefix2 = SseMessageTypeEnum.OUTLINE_AGENT_STREAMING.get_streaming_prefix()
        streaming_prefix3 = SseMessageTypeEnum.CONTENT_AGENT_STREAMING.get_streaming_prefix()
        image_complete_prefix = SseMessageTypeEnum.IMAGE_COMPLETE.get_streaming_prefix()
        
        if message.startswith(streaming_prefix2):
            return {"type": SseMessageTypeEnum.OUTLINE_AGENT_STREAMING.value,
                    "content": message[len(streaming_prefix2):]}
        
        if message.startswith(streaming_prefix3):
            return {"type": SseMessageTypeEnum.CONTENT_AGENT_STREAMING.value,
                    "content": message[len(streaming_prefix3):]}
        
        if message.startswith(image_complete_prefix):
            image_json = message[len(image_complete_prefix):]
            return {"type": SseMessageTypeEnum.IMAGE_COMPLETE.value,
                    "image": json.loads(image_json)}
        
        # 处理完成消息（枚举值）
        return self._build_complete_message_data(message, state)


# 全局单例
blog_async_service = BlogAsyncService()
