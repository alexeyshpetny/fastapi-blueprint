from src.adapters.redis_adapter import RedisAdapter
from src.adapters.request_adapter import RequestCacheAdapter
from src.cache.redis import cache_client
from src.core.settings import settings


def get_request_cache_adapter(
    enabled: bool,
    cache_enabled: bool,
    ttl: int,
    exclude_paths: list[str],
    key_prefix: str,
) -> RequestCacheAdapter | None:
    if not settings.CACHE_ENABLED:
        return None
    redis_adapter = RedisAdapter(cache_client)
    return RequestCacheAdapter(
        redis_adapter=redis_adapter,
        enabled=enabled,
        cache_enabled=cache_enabled,
        ttl=ttl,
        exclude_paths=exclude_paths,
        key_prefix=key_prefix,
    )
