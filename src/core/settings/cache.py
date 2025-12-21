from pydantic import Field
from pydantic_settings import BaseSettings


class CacheSettings(BaseSettings):
    CACHE_ENABLED: bool = Field(
        default=True,
        description="Enable Redis cache. Set to False to disable caching.",
    )
    CACHE_HOST: str = Field(
        default="localhost",
        description="Redis cache host",
    )
    CACHE_PORT: int = Field(
        default=6379,
        ge=1,
        le=65535,
        description="Redis cache port",
    )
    CACHE_PASSWORD: str | None = Field(
        default=None,
        description="Redis cache password (optional)",
    )
    CACHE_DB: int = Field(
        default=0,
        ge=0,
        le=15,
        description="Redis database number (0-15)",
    )
    CACHE_DECODE_RESPONSES: bool = Field(
        default=True,
        description="Automatically decode Redis responses to strings",
    )
    CACHE_SOCKET_TIMEOUT: int = Field(
        default=5,
        ge=1,
        description="Socket timeout in seconds for Redis operations",
    )
    CACHE_SOCKET_CONNECT_TIMEOUT: int = Field(
        default=5,
        ge=1,
        description="Socket connection timeout in seconds",
    )
    CACHE_MAX_CONNECTIONS: int = Field(
        default=50,
        ge=1,
        description="Maximum number of connections in the Redis connection pool",
    )
    CACHE_RETRY_ON_TIMEOUT: bool = Field(
        default=True,
        description="Retry operations on timeout",
    )
    CACHE_DEFAULT_TTL: int = Field(
        default=3600,
        ge=1,
        description="Default time-to-live for cached items in seconds",
    )

    @property
    def cache_url(self: "CacheSettings") -> str:
        if self.CACHE_PASSWORD:
            return f"redis://:{self.CACHE_PASSWORD}@{self.CACHE_HOST}:{self.CACHE_PORT}/{self.CACHE_DB}"
        return f"redis://{self.CACHE_HOST}:{self.CACHE_PORT}/{self.CACHE_DB}"
