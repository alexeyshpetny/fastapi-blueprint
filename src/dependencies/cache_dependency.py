from src.adapters.cache_adapter import RedisCacheAdapter
from src.adapters.request_cache_adapter import RedisRequestCacheAdapter
from src.cache.redis import cache_client


def get_cache_adapter() -> RedisCacheAdapter | None:
    if cache_client is None:
        return None
    return RedisCacheAdapter(cache_client)


def get_request_cache_adapter(
    enabled: bool,
    cache_enabled: bool,
    ttl: int,
    exclude_paths: list[str],
    key_prefix: str,
) -> RedisRequestCacheAdapter | None:
    cache_adapter = get_cache_adapter()
    if cache_adapter is None:
        return None
    return RedisRequestCacheAdapter(
        cache_adapter=cache_adapter,
        enabled=enabled,
        cache_enabled=cache_enabled,
        ttl=ttl,
        exclude_paths=exclude_paths,
        key_prefix=key_prefix,
    )
