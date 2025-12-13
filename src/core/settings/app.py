from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    API_V1_PREFIX: str = Field(
        default="/api/v1",
        description="URL prefix for API v1 endpoints",
        pattern=r"^/.*",
    )

    TESTING: bool = Field(
        default=False,
        description="Enable testing mode. Auto-set to True during pytest execution.",
    )

    DEBUG: bool = Field(
        default=False,
        description=(
            "Enable debug mode (shows detailed error pages with stack traces). "
            "WARNING: Never enable in production for security reasons."
        ),
    )

    DOC_TITLE: str = Field(
        default="Shpetny FastAPI Blueprint",
        description="Title of the API documentation",
    )
    DOC_VERSION: str = Field(
        default="1.0.0",
        description="API version displayed in documentation",
    )
    DOC_DESCRIPTION: str = Field(
        default="API documentation for Shpetny FastAPI Blueprint",
        description="Description of the API shown in documentation",
    )
    DOC_OPENAPI_URL: str = Field(
        default="/api/openapi.json",
        description="URL path for OpenAPI JSON schema",
        pattern=r"^/.*",
    )
    DOC_OPENAPI_VERSION: str = Field(
        default="3.0.2",
        description="OpenAPI specification version",
    )
    DOC_SWAGGER_URL: str = Field(
        default="/api/docs",
        description="URL path for Swagger UI documentation",
        pattern=r"^/.*",
    )
    DOC_REDOC_URL: str = Field(
        default="/api/redoc",
        description="URL path for ReDoc documentation",
        pattern=r"^/.*",
    )

    CORS_ALLOW_ORIGINS: list[str] = Field(
        default=["*"],
        description=(
            "List of allowed CORS origins (use ['*'] for all origins). "
            "WARNING: Change to specific origins in production for security."
        ),
    )
    CORS_ALLOW_METHODS: list[str] = Field(
        default=["*"],
        description="List of allowed HTTP methods for CORS (use ['*'] for all methods)",
    )
    CORS_ALLOW_HEADERS: list[str] = Field(
        default=["*"],
        description="List of allowed HTTP headers for CORS (use ['*'] for all headers)",
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=False,
        description="Whether to allow credentials in CORS requests",
    )
    CORS_MAX_AGE: int = Field(
        default=600,
        ge=0,
        description="Maximum age (in seconds) for CORS preflight requests",
    )
