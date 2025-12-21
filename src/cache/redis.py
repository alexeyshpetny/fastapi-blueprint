import logging

from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool
from redis.exceptions import RedisError

from src.core.settings import settings

logger = logging.getLogger(__name__)


class Cache:
    def __init__(self) -> None:
        self._client: Redis | None = None
        self._pool: ConnectionPool | None = None

    @property
    def client(self) -> Redis | None:
        return self._client

    async def init(self) -> None:
        if not settings.CACHE_ENABLED:
            logger.info("Cache is disabled, skipping initialization")
            return

        self._pool = ConnectionPool.from_url(
            settings.cache_url,
            max_connections=settings.CACHE_MAX_CONNECTIONS,
            decode_responses=settings.CACHE_DECODE_RESPONSES,
            socket_timeout=settings.CACHE_SOCKET_TIMEOUT,
            socket_connect_timeout=settings.CACHE_SOCKET_CONNECT_TIMEOUT,
            retry_on_timeout=settings.CACHE_RETRY_ON_TIMEOUT,
        )
        self._client = Redis(connection_pool=self._pool)

        try:
            await self._client.ping()
            logger.info("Successfully connected to Redis cache")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}", exc_info=True)
            self._client = None
            if self._pool is not None:
                await self._pool.aclose()
                self._pool = None

    async def close(self) -> None:
        if self._client is None:
            return

        try:
            await self._client.aclose()
            if self._pool is not None:
                await self._pool.aclose()
            logger.info("Disconnected from Redis cache")
        except RedisError as e:
            logger.warning(f"Error disconnecting from Redis: {e}", exc_info=True)
        finally:
            self._client = None
            self._pool = None


cache = Cache()
