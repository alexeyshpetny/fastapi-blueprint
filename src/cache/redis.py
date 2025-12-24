import logging

from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from src.core.settings import settings

logger = logging.getLogger(__name__)

cache_pool: ConnectionPool | None
cache_client: Redis | None

if settings.CACHE_ENABLED:
    cache_pool = ConnectionPool.from_url(
        settings.cache_url,
        max_connections=settings.CACHE_MAX_CONNECTIONS,
        decode_responses=False,
        socket_timeout=settings.CACHE_SOCKET_TIMEOUT,
        socket_connect_timeout=settings.CACHE_SOCKET_CONNECT_TIMEOUT,
        retry_on_timeout=settings.CACHE_RETRY_ON_TIMEOUT,
    )
    cache_client = Redis(connection_pool=cache_pool)
else:
    cache_pool = None
    cache_client = None


async def close_cache() -> None:
    if not settings.CACHE_ENABLED:
        return
    try:
        if cache_client is not None:
            await cache_client.aclose()
        if cache_pool is not None:
            await cache_pool.aclose()
        logger.info("Disconnected from Redis cache")
    except Exception as e:
        logger.warning(f"Error disconnecting from Redis: {e}", exc_info=True)
