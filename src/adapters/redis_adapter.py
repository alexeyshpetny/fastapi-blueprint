import json
import logging
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import ConnectionError, RedisError, TimeoutError

from src.core.settings import settings
from src.utils.decorators import handle_exceptions

logger = logging.getLogger(__name__)

REDIS_EXCEPTIONS = (ConnectionError, TimeoutError, RedisError)


class RedisAdapter:
    def __init__(self, redis_client: Redis | None) -> None:
        self._redis = redis_client

    def _validate_key(self, key: str) -> bool:
        if not key or not isinstance(key, str):
            logger.warning(f"Invalid cache key: {key!r}")
            return False
        return True

    def _validate_ttl(self, ttl: int) -> bool:
        if not (settings.CACHE_MIN_TTL <= ttl <= settings.CACHE_MAX_TTL):
            logger.warning(
                f"Invalid TTL value: {ttl}, must be between {settings.CACHE_MIN_TTL} and {settings.CACHE_MAX_TTL}"
            )
            return False
        return True

    def _serialize_value(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)

    def _deserialize_value(self, value: str) -> Any:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    @handle_exceptions(REDIS_EXCEPTIONS, default=None)
    async def get(self, key: str) -> Any | None:
        if not self._validate_key(key) or self._redis is None:
            return None

        value = await self._redis.get(key)
        if value is None:
            return None
        return self._deserialize_value(value) if isinstance(value, str) else value

    @handle_exceptions(REDIS_EXCEPTIONS, default=False)
    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        if not self._validate_key(key) or self._redis is None:
            return False

        if ttl is not None and not self._validate_ttl(ttl):
            return False

        serialized = self._serialize_value(value)
        effective_ttl = ttl if ttl is not None else settings.CACHE_DEFAULT_TTL
        await self._redis.setex(key, effective_ttl, serialized)
        return True

    @handle_exceptions(REDIS_EXCEPTIONS, default=False)
    async def delete(self, key: str) -> bool:
        if not self._validate_key(key) or self._redis is None:
            return False

        result = await self._redis.delete(key)
        return bool(result)

    @handle_exceptions(REDIS_EXCEPTIONS, default=0)
    async def delete_pattern(self, pattern: str) -> int:
        if not pattern or not isinstance(pattern, str):
            logger.warning(f"Invalid cache pattern: {pattern!r}")
            return 0

        if self._redis is None:
            return 0

        keys = [key async for key in self._redis.scan_iter(match=pattern)]
        if not keys:
            return 0
        deleted = await self._redis.delete(*keys)
        return deleted if isinstance(deleted, int) else 0

    @handle_exceptions(REDIS_EXCEPTIONS, default=False)
    async def exists(self, key: str) -> bool:
        if not self._validate_key(key) or self._redis is None:
            return False

        result = await self._redis.exists(key)
        return bool(result)

    @handle_exceptions(REDIS_EXCEPTIONS, default=False)
    async def expire(self, key: str, ttl: int) -> bool:
        if not self._validate_key(key) or not self._validate_ttl(ttl) or self._redis is None:
            return False

        result = await self._redis.expire(key, ttl)
        return bool(result)
