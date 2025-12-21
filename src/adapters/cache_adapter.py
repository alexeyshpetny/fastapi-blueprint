import json
import logging
from typing import Any, Protocol

from redis.asyncio import Redis
from redis.exceptions import ConnectionError, RedisError, TimeoutError

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
        if not key or not isinstance(key, str):
            logger.warning(f"Invalid cache key: {key!r}")
            return None

        if self._redis is None:
            return None

        try:
            value = await self._redis.get(key)
            if value is None:
                return None

            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return value
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Cache connection error for key '{key}': {e}", exc_info=True)
            return None
        except RedisError as e:
            logger.warning(f"Cache get error for key '{key}': {e}", exc_info=True)
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        if not key or not isinstance(key, str):
            logger.warning(f"Invalid cache key: {key!r}")
            return False

        if self._redis is None:
            return False

        if ttl is not None and (ttl < 1 or ttl > 2147483647):
            logger.warning(f"Invalid TTL value: {ttl}, must be between 1 and 2147483647")
            return False

        try:
            if isinstance(value, str):
                serialized_value = value
            else:
                serialized_value = json.dumps(value, ensure_ascii=False)

            ttl = ttl if ttl is not None else settings.CACHE_DEFAULT_TTL
            await self._redis.setex(key, ttl, serialized_value)
            return True
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Cache connection error for key '{key}': {e}", exc_info=True)
            return False
        except (RedisError, TypeError, ValueError) as e:
            logger.warning(f"Cache set error for key '{key}': {e}", exc_info=True)
            return False

    async def delete(self, key: str) -> bool:
        if not key or not isinstance(key, str):
            logger.warning(f"Invalid cache key: {key!r}")
            return False

        if self._redis is None:
            return False

        try:
            result = await self._redis.delete(key)
            return bool(result)
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Cache connection error for key '{key}': {e}", exc_info=True)
            return False
        except RedisError as e:
            logger.warning(f"Cache delete error for key '{key}': {e}", exc_info=True)
            return False

    async def delete_pattern(self, pattern: str) -> int:
        if not pattern or not isinstance(pattern, str):
            logger.warning(f"Invalid cache pattern: {pattern!r}")
            return 0

        if self._redis is None:
            return 0

        try:
            keys = [key async for key in self._redis.scan_iter(match=pattern)]
            if not keys:
                return 0
            deleted = await self._redis.delete(*keys)
            return deleted if isinstance(deleted, int) else 0
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Cache connection error for pattern '{pattern}': {e}", exc_info=True)
            return 0
        except RedisError as e:
            logger.warning(f"Cache delete_pattern error for pattern '{pattern}': {e}", exc_info=True)
            return 0

    async def exists(self, key: str) -> bool:
        if not key or not isinstance(key, str):
            return False

        if self._redis is None:
            return False

        try:
            result = await self._redis.exists(key)
            return bool(result)
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Cache connection error for key '{key}': {e}", exc_info=True)
            return False
        except RedisError as e:
            logger.warning(f"Cache exists error for key '{key}': {e}", exc_info=True)
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        if not key or not isinstance(key, str):
            return False

        if self._redis is None:
            return False

        if ttl < 1 or ttl > 2147483647:
            logger.warning(f"Invalid TTL value: {ttl}, must be between 1 and 2147483647")
            return False

        try:
            result = await self._redis.expire(key, ttl)
            return bool(result)
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Cache connection error for key '{key}': {e}", exc_info=True)
            return False
        except RedisError as e:
            logger.warning(f"Cache expire error for key '{key}': {e}", exc_info=True)
            return False
