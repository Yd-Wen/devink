"""Session 管理工具"""
"""
将 Session 存储到 Redis 有两个好处:
- 首先，服务重启后登录状态不会丢失，不用每次调试都重新登录;
- 其次，如果以后部署多台服务器，所有服务器共享同一个Redis，用户在任意一台机器上都能保持登录。
"""
import redis.asyncio as redis
import json
from typing import Optional, Any
from app.config import settings

# Redis 连接池
redis_client: Optional[redis.Redis] = None


async def init_redis():
    """初始化 Redis 连接"""
    global redis_client
    redis_client = redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True
    )


async def close_redis():
    """关闭 Redis 连接"""
    global redis_client
    if redis_client:
        await redis_client.close()


def _get_session_key(session_id: str) -> str:
    """获取 Session Key"""
    return f"session:{session_id}"


async def get_session(session_id: str) -> Optional[dict]:
    """获取 Session 数据"""
    if not redis_client:
        return None
    
    key = _get_session_key(session_id)
    data = await redis_client.get(key)
    
    if data:
        return json.loads(data)
    return None


async def set_session(session_id: str, data: dict, expire: Optional[int] = None):
    """设置 Session 数据"""
    if not redis_client:
        return
    
    key = _get_session_key(session_id)
    expire_time = expire or settings.session_max_age
    
    await redis_client.setex(
        key,
        expire_time,
        json.dumps(data) # value
    )


async def remove_session(session_id: str):
    """删除 Session"""
    if not redis_client:
        return
    
    key = _get_session_key(session_id)
    await redis_client.delete(key)
