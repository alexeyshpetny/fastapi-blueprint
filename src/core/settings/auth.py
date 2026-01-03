import logging
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class AuthSettings(BaseSettings):
    JWT_SECRET_KEY: str = Field(
        default="change-me-in-production-minimum-32-characters-long-secret-key",
        description="Secret key for signing JWT tokens. Must be at least 32 characters in production.",
        min_length=32,
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        ge=1,
        description="Access token expiration in minutes",
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        ge=1,
        description="Refresh token expiration in days",
    )
    JWT_REFRESH_TOKEN_COOKIE_NAME: str = Field(
        default="refresh_token",
        description="Cookie name for refresh token",
    )
    JWT_REFRESH_TOKEN_HTTP_ONLY: bool = Field(
        default=True,
        description="HTTP-only cookie flag (XSS protection)",
    )
    JWT_REFRESH_TOKEN_SECURE: bool = Field(
        default=False,
        description="Secure cookie flag (HTTPS only). Set to False for local development (HTTP).",
    )
    JWT_REFRESH_TOKEN_SAME_SITE: Literal[
        "lax",
        "strict",
        "none",
    ] = Field(
        default="lax",
        description="SameSite cookie attribute: strict, lax, or none",
    )
    PASSWORD_MIN_LENGTH: int = Field(
        default=8,
        ge=6,
        description="Minimum password length",
    )
    BCRYPT_ROUNDS: int = Field(
        default=12,
        ge=10,
        le=20,
        description="Bcrypt hashing rounds",
    )
    DEFAULT_USER_ROLE: str = Field(
        default="user",
        description="Default role for new users",
    )

    @property
    def JWT_ACCESS_TOKEN_EXPIRE_SECONDS(self) -> int:
        return self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

    @property
    def JWT_REFRESH_TOKEN_EXPIRE_SECONDS(self) -> int:
        return self.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    def model_post_init(self, _) -> None:
        if not getattr(self, "is_production", False):
            return

        default_secret = "change-me-in-production-minimum-32-characters-long-secret-key"
        if self.JWT_SECRET_KEY == default_secret:
            raise ValueError(
                "JWT_SECRET_KEY must be changed from default in production. "
                "Use a secure random string (32+ characters) from a secret management service."
            )

        if len(self.JWT_SECRET_KEY) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters in production.")

        if self.JWT_REFRESH_TOKEN_SAME_SITE == "none" and not self.JWT_REFRESH_TOKEN_SECURE:
            raise ValueError("JWT_REFRESH_TOKEN_SAME_SITE='none' requires JWT_REFRESH_TOKEN_SECURE=True")

        if not self.JWT_REFRESH_TOKEN_SECURE:
            logger.warning("JWT_REFRESH_TOKEN_SECURE is False in production. Use HTTPS for security.")
