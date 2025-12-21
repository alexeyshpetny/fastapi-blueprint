import hashlib
import json
import logging

from fastapi import Request, Response

from src.adapters.redis_adapter import RedisAdapter
from src.core.settings import settings

logger = logging.getLogger(__name__)


class RequestCacheAdapter:
    def __init__(
        self,
        redis_adapter: RedisAdapter,
        enabled: bool,
        cache_enabled: bool,
        ttl: int,
        exclude_paths: list[str],
        key_prefix: str,
    ) -> None:
        self.redis_adapter = redis_adapter
        self.enabled = enabled and cache_enabled
        self.ttl = ttl
        self.exclude_paths = exclude_paths
        self.key_prefix = key_prefix

    def _filter_sensitive_headers(self, headers: dict[str, str]) -> dict[str, str]:
        return {
            key: value
            for key, value in headers.items()
            if key.lower() not in settings.CACHE_SENSITIVE_HEADERS and not key.lower().startswith("x-cache")
        }

    def _is_cacheable_response(self, response: Response) -> bool:
        return response.status_code == 200 and response.headers.get("content-type", "").startswith("application/json")

    def should_cache(self, request: Request) -> bool:
        if not self.enabled or request.method != "GET":
            return False

        if request.headers.get("X-Cache-Bypass", "").lower() == "true":
            return False

        path = request.url.path
        return not any(path.startswith(excluded) for excluded in self.exclude_paths)

    def generate_cache_key(self, request: Request) -> str:
        query_string = str(request.query_params) if request.query_params else ""
        key_data = f"{request.method}:{request.url.path}:{query_string}"
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()
        return f"{self.key_prefix}:{key_hash}"

    async def get_cached_response(self, cache_key: str, path: str) -> Response | None:
        cached_data = await self.redis_adapter.get(cache_key)
        if cached_data is None:
            logger.debug(f"Cache miss for key: {cache_key}", extra={"path": path})
            return None

        if not isinstance(cached_data, dict) or not settings.CACHE_REQUIRED_FIELDS.issubset(cached_data):
            logger.warning(f"Invalid cached data for key '{cache_key}'", extra={"path": path})
            return None

        try:
            response = Response(
                content=json.dumps(cached_data["body"], ensure_ascii=False).encode("utf-8"),
                status_code=int(cached_data["status_code"]),
                headers=dict(cached_data["headers"]),
                media_type="application/json",
            )
            response.headers["X-Cache"] = "HIT"
            logger.debug(f"Cache hit for key: {cache_key}", extra={"path": path})
            return response
        except (ValueError, TypeError, KeyError, json.JSONEncodeError) as e:
            logger.warning(f"Error deserializing cached response for key '{cache_key}': {e}", exc_info=True)
            return None

    async def cache_response(
        self,
        cache_key: str,
        response: Response,
        path: str,
    ) -> Response:
        if not self._is_cacheable_response(response):
            response.headers["X-Cache"] = "SKIP"
            return response

        try:
            response_body = await response.body()
            if not response_body:
                response.headers["X-Cache"] = "SKIP"
                return response

            body_data = json.loads(response_body.decode("utf-8"))
            await self.redis_adapter.set(
                cache_key,
                {
                    "status_code": response.status_code,
                    "headers": self._filter_sensitive_headers(dict(response.headers)),
                    "body": body_data,
                },
                ttl=self.ttl,
            )
            logger.debug(f"Cached response for key: {cache_key}", extra={"path": path})
            response.headers["X-Cache"] = "MISS"
            return response
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to cache response for key '{cache_key}': {e}", extra={"path": path})
            response.headers["X-Cache"] = "SKIP"
            return response
        except Exception as e:
            logger.warning(f"Cache store error for key '{cache_key}': {e}", exc_info=True)
            response.headers["X-Cache"] = "ERROR"
            return response
