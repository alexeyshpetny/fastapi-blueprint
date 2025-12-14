from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    DB_HOST: str = Field(
        default="localhost",
        description="PostgreSQL database host",
    )
    DB_PORT: int = Field(
        default=5432,
        ge=1,
        le=65535,
        description="PostgreSQL database port",
    )
    DB_USER: str = Field(
        default="postgres",
        description="PostgreSQL database user",
    )
    DB_PASSWORD: str = Field(
        default="postgres",
        description="PostgreSQL database password",
    )
    DB_NAME: str = Field(
        default="shpetny_fastapi_blueprint",
        description="PostgreSQL database name",
    )
    DB_POOL_SIZE: int = Field(
        default=5,
        ge=1,
        description="Database connection pool size",
    )
    DB_MAX_OVERFLOW: int = Field(
        default=10,
        ge=0,
        description="Maximum number of connections to allow in addition to pool_size",
    )
    DB_POOL_TIMEOUT: int = Field(
        default=30,
        ge=1,
        description="Timeout in seconds for getting a connection from the pool",
    )
    DB_POOL_RECYCLE: int = Field(
        default=3600,
        ge=1,
        description="Number of seconds after which a connection is recycled",
    )
    DB_ECHO: bool = Field(
        default=False,
        description="Enable SQLAlchemy query logging (useful for debugging)",
    )

    @property
    def db_url(self: "DatabaseSettings") -> str:
        """Build db URL with properly encoded credentials."""
        user = quote_plus(self.DB_USER)
        password = quote_plus(self.DB_PASSWORD)
        return f"postgresql+asyncpg://{user}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
