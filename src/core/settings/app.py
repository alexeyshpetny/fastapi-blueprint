import logging
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class AppSettings(BaseSettings):
    API_V1_PREFIX: str = Field(
        default="/api/v1",
        description="URL prefix for API v1 endpoints",
        pattern=r"^/.*",
    )

    ENVIRONMENT: Literal[
        "production",
        "development",
        "testing",
    ] = Field(
        default="development",
        description=(
            "Application environment: 'production', 'development', or 'testing'. "
            "Used for validation and security checks."
        ),
    )

    DEBUG: bool = Field(
        default=False,
        description=(
            "Enable FastAPI debug mode (shows detailed error pages with stack traces). "
            "WARNING: Never enable in production for security reasons."
        ),
    )

    SERVICE_NAME: str = Field(
        default="fastapi-blueprint",
        description="Name of the service used in health checks and responses",
    )

    DOC_TITLE: str = Field(
        default="FastAPI Blueprint",
        description="Title of the API documentation",
    )
    DOC_VERSION: str = Field(
        default="1.0.0",
        description="API version displayed in documentation",
    )
    DOC_DESCRIPTION: str = Field(
        default="API documentation for FastAPI Blueprint",
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
            "List of allowed CORS origins. "
            "WARNING: ['*'] allows all origins and is insecure for production. "
            "Use specific origins like ['https://example.com', 'https://app.example.com'] in production. "
            "Cannot use ['*'] with CORS_ALLOW_CREDENTIALS=True."
        ),
    )
    CORS_ALLOW_METHODS: list[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        description=(
            "List of allowed HTTP methods for CORS. "
            "Default: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']. "
            "Use ['*'] to allow all methods (not recommended for production)."
        ),
    )
    CORS_ALLOW_HEADERS: list[str] = Field(
        default=["*"],
        description=(
            "List of allowed HTTP headers for CORS. "
            "Use ['*'] to allow all headers, or specify: ['Content-Type', 'Authorization', 'X-Request-ID']"
        ),
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=False,
        description=(
            "Whether to allow credentials in CORS requests. "
            "WARNING: Cannot be True if CORS_ALLOW_ORIGINS contains ['*']."
        ),
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

    TRUSTED_HOSTS_ENABLED: bool = Field(
        default=False,
        description="Enable TrustedHostMiddleware to validate Host header (prevents host header injection attacks)",
    )
    TRUSTED_HOSTS: list[str] = Field(
        default=[],
        description=(
            "List of trusted hosts (e.g., ['example.com', '*.example.com']). "
            "Required if TRUSTED_HOSTS_ENABLED=True. "
            "Use ['*'] to allow all hosts (not recommended for production)."
        ),
    )
    MAX_REQUEST_BODY_SIZE: int = Field(
        default=10485760,
        ge=1024,
        description="Maximum request body size in bytes (default: 10MB). Prevents DoS via large payloads.",
    )

    @field_validator("ENVIRONMENT", mode="before")
    @classmethod
    def normalize_environment(cls, v: str) -> str:
        return v.lower() if isinstance(v, str) else v

    @property
    def is_production(self) -> bool:
        return getattr(self, "ENVIRONMENT", "development") == "production"

    def model_post_init(self, _) -> None:
        if not self.CORS_ALLOW_ORIGINS:
            raise ValueError("CORS_ALLOW_ORIGINS cannot be empty")

        if not self.is_production:
            return

        if self.DEBUG:
            raise ValueError("DEBUG=True is not allowed in production. This exposes sensitive error information.")

        if self.CORS_ALLOW_ORIGINS == ["*"]:
            raise ValueError(
                "CORS_ALLOW_ORIGINS=['*'] is not allowed in production. Specify allowed origins for security."
            )

        if self.CORS_ALLOW_CREDENTIALS and self.CORS_ALLOW_ORIGINS == ["*"]:
            raise ValueError(
                "CORS_ALLOW_CREDENTIALS cannot be True when CORS_ALLOW_ORIGINS is ['*']. "
                "This is a security risk. Use specific origins instead."
            )

        if self.TRUSTED_HOSTS_ENABLED and not self.TRUSTED_HOSTS:
            raise ValueError(
                "TRUSTED_HOSTS_ENABLED=True requires TRUSTED_HOSTS to be set. "
                "Provide a list of allowed hosts (e.g., ['example.com', '*.example.com'])."
            )
