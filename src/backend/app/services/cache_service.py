import json
import logging
from typing import Any, Optional
import redis.asyncio as redis
from ..config import settings

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self):
        self._client: Optional[redis.Redis] = None

    async def get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self._client

    async def get(self, key: str) -> Optional[Any]:
        try:
            client = await self.get_client()
            value = await client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
        return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        try:
            client = await self.get_client()
            await client.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
        return False

    async def delete(self, key: str) -> bool:
        try:
            client = await self.get_client()
            await client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
        return False

    async def delete_pattern(self, pattern: str) -> int:
        try:
            client = await self.get_client()
            keys = await client.keys(pattern)
            if keys:
                return await client.delete(*keys)
        except Exception as e:
            logger.warning(f"Cache delete_pattern error for pattern {pattern}: {e}")
        return 0

    async def close(self):
        if self._client:
            await self._client.close()
            self._client = None


cache_service = CacheService()
