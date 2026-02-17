from typing import Any, Optional
from redis.asyncio import Redis
import json
import asyncio

class CacheManager:
    def __init__(self, refis_client: Redis, default_ttl: int = 600):
        self.redis = redis_client
        self.ttl = default_ttl

    async def get(self, key: str) -> Optional[Any]:
        """Getting object in cache"""
        data = await.self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int]=600):
        """Saving object into cache"""
        ttl = ttl or self.ttl
        data =  json.dumps(value)
        await self.redis.set(key, data, ex=ttl)

    async def invalidate(self, key:str):
        """Removing key from cache"""
        await self.redis.delete(key)

    async def get_or_set(self, key:str, fetch_func, ttl: Optional[int] = None):
        """Get if not exist define fetch_func"""
        cached = await self.get(key)
        if cached is not None:
            return cached

        result = await fetch_func()
        if result is not None:
            await self.set(key, result, ttl=ttl)
        return result
