import json
import logging
from typing import Any, Protocol

from redis.asyncio import Redis
from redis.exceptions import RedisError

from src.core.settings import settings

logger = logging.getLogger(__name__)


class CacheAdapter(Protocol):
    async def get(self, key: str) -> Any | None: ...

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool: ...

    async def delete(self, key: str) -> bool: ...

    async def delete_pattern(self, pattern: str) -> int: ...

    async def exists(self, key: str) -> bool: ...

    async def expire(self, key: str, ttl: int) -> bool: ...


class RedisCacheAdapter:
    def __init__(self, redis_client: Redis | None) -> None:
        self._redis = redis_client

    async def get(self, key: str) -> Any | None:
        if self._redis is None:
            return None

        try:
            value = await self._redis.get(key)
            if value is None:
                return None
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except RedisError as e:
            logger.warning(f"Cache get error for key '{key}': {e}", exc_info=True)
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        if self._redis is None:
            return False

        try:
            serialized_value = value if isinstance(value, str) else json.dumps(value)
            ttl = ttl if ttl is not None else settings.CACHE_DEFAULT_TTL
            await self._redis.setex(key, ttl, serialized_value)
            return True
        except (RedisError, TypeError) as e:
            logger.warning(f"Cache set error for key '{key}': {e}", exc_info=True)
            return False

    async def delete(self, key: str) -> bool:
        if self._redis is None:
            return False

        try:
            result = await self._redis.delete(key)
            return bool(result)
        except RedisError as e:
            logger.warning(f"Cache delete error for key '{key}': {e}", exc_info=True)
            return False

    async def delete_pattern(self, pattern: str) -> int:
        if self._redis is None:
            return 0

        try:
            keys = [key async for key in self._redis.scan_iter(match=pattern)]
            return await self._redis.delete(*keys) if keys else 0
        except RedisError as e:
            logger.warning(f"Cache delete_pattern error for pattern '{pattern}': {e}", exc_info=True)
            return 0

    async def exists(self, key: str) -> bool:
        if self._redis is None:
            return False

        try:
            return bool(await self._redis.exists(key))
        except RedisError as e:
            logger.warning(f"Cache exists error for key '{key}': {e}", exc_info=True)
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        if self._redis is None:
            return False

        try:
            return bool(await self._redis.expire(key, ttl))
        except RedisError as e:
            logger.warning(f"Cache expire error for key '{key}': {e}", exc_info=True)
            return False
