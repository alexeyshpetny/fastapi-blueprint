import hashlib
import json
import logging
from typing import Protocol

from fastapi import Request, Response

from src.adapters.cache_adapter import CacheAdapter

logger = logging.getLogger(__name__)

SENSITIVE_HEADERS = {
    "authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "x-auth-token",
    "x-csrf-token",
    "x-request-id",
    "x-trace-id",
}


class RequestCacheAdapter(Protocol):
    def should_cache(self, request: Request) -> bool: ...

    def generate_cache_key(self, request: Request) -> str: ...

    async def get_cached_response(self, cache_key: str, path: str) -> Response | None: ...

    async def cache_response(self, cache_key: str, response: Response, path: str) -> Response: ...


class RedisRequestCacheAdapter:
    def __init__(
        self,
        cache_adapter: CacheAdapter,
        enabled: bool,
        cache_enabled: bool,
        ttl: int,
        exclude_paths: list[str],
        key_prefix: str,
    ) -> None:
        self.cache_adapter = cache_adapter
        self.enabled = enabled and cache_enabled
        self.ttl = ttl
        self.exclude_paths = exclude_paths
        self.key_prefix = key_prefix

    def should_cache(self, request: Request) -> bool:
        if not self.enabled:
            return False

        if request.method != "GET":
            return False

        if request.headers.get("X-Cache-Bypass", "").lower() == "true":
            return False

        path = request.url.path
        for excluded_path in self.exclude_paths:
            if path.startswith(excluded_path):
                return False

        return True

    def generate_cache_key(self, request: Request) -> str:
        path = request.url.path
        query_string = str(request.query_params) if request.query_params else ""
        key_data = f"{request.method}:{path}:{query_string}"
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()
        return f"{self.key_prefix}:{key_hash}"

    def _filter_sensitive_headers(self, headers: dict[str, str]) -> dict[str, str]:
        return {
            key: value
            for key, value in headers.items()
            if key.lower() not in SENSITIVE_HEADERS and not key.lower().startswith("x-cache")
        }

    async def get_cached_response(self, cache_key: str, path: str) -> Response | None:
        cached_data = await self.cache_adapter.get(cache_key)
        if cached_data is None:
            logger.debug(f"Cache miss for key: {cache_key}", extra={"path": path})
            return None

        if not isinstance(cached_data, dict) or not all(
            key in cached_data for key in ("status_code", "headers", "body")
        ):
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
        if response.status_code != 200 or not response.headers.get("content-type", "").startswith("application/json"):
            response.headers["X-Cache"] = "SKIP"
            return response

        try:
            response_body = await response.body()
            if not response_body:
                response.headers["X-Cache"] = "SKIP"
                return response

            body_data = json.loads(response_body.decode("utf-8"))
            await self.cache_adapter.set(
                cache_key,
                {
                    "status_code": response.status_code,
                    "headers": self._filter_sensitive_headers(dict(response.headers)),
                    "body": body_data,
                },
                ttl=self.ttl,
            )
            logger.debug(f"Cached response for key: {cache_key}", extra={"path": path})

            return Response(
                content=response_body,
                status_code=response.status_code,
                headers={**dict(response.headers), "X-Cache": "MISS"},
                media_type=response.media_type,
            )
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to cache response for key '{cache_key}': {e}", extra={"path": path})
            response.headers["X-Cache"] = "SKIP"
            return response
        except Exception as e:
            logger.warning(f"Cache store error for key '{cache_key}': {e}", exc_info=True)
            response.headers["X-Cache"] = "ERROR"
            return response
