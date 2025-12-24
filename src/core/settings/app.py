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

    SERVICE_NAME: str = Field(
        default="shpetny-fastapi-blueprint",
        description="Name of the service used in health checks and responses",
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

    SECURITY_HEADERS_ENABLED: bool = Field(
        default=True,
        description="Enable security headers middleware",
    )
    SECURITY_X_CONTENT_TYPE_OPTIONS: str = Field(
        default="nosniff",
        description="X-Content-Type-Options header value (prevents MIME type sniffing)",
    )
    SECURITY_X_FRAME_OPTIONS: str = Field(
        default="DENY",
        description="X-Frame-Options header value (prevents clickjacking). Options: DENY, SAMEORIGIN, ALLOW-FROM",
    )
    SECURITY_X_XSS_PROTECTION: str = Field(
        default="1; mode=block",
        description="X-XSS-Protection header value (enables XSS filter in older browsers)",
    )
    SECURITY_STRICT_TRANSPORT_SECURITY: str | None = Field(
        default=None,
        description=(
            "Strict-Transport-Security header value (HSTS). "
            "Example: 'max-age=31536000; includeSubDomains'. "
            "Only set this if your application is served over HTTPS."
        ),
    )
    SECURITY_CONTENT_SECURITY_POLICY: str | None = Field(
        default=None,
        description=(
            "Content-Security-Policy header value. "
            "Example: \"default-src 'self'; script-src 'self' 'unsafe-inline'\". "
            "If None, header is not set (allows flexibility for API-only services)."
        ),
    )
    SECURITY_REFERRER_POLICY: str = Field(
        default="strict-origin-when-cross-origin",
        description=("Referrer-Policy header value. Controls how much referrer information is sent with requests."),
    )
    SECURITY_PERMISSIONS_POLICY: str | None = Field(
        default=None,
        description=(
            "Permissions-Policy header value. "
            "Controls browser features and APIs. "
            "Example: 'geolocation=(), microphone=(), camera=()'"
        ),
    )

    RATE_LIMIT_ENABLED: bool = Field(
        default=False,
        description="Enable rate limiting middleware",
    )
    RATE_LIMIT_DEFAULT: str = Field(
        default="100/minute",
        description="Default rate limit for all endpoints (format: 'count/period', e.g., '100/minute', '10/second')",
    )
    RATE_LIMIT_STORAGE_URI: str | None = Field(
        default=None,
        description=(
            "Redis URI for rate limiting storage. "
            "If None, uses in-memory storage (not recommended for production with multiple workers). "
            "Example: 'redis://localhost:6379/1'"
        ),
    )
    RATE_LIMIT_HEADERS_ENABLED: bool = Field(
        default=True,
        description="Include rate limit headers in responses (X-RateLimit-Limit, X-RateLimit-Remaining, etc.)",
    )
