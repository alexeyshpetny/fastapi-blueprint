from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from src.core.settings import settings


class LoginRequest(BaseModel):
    email: EmailStr = Field(description="User email address")
    password: str = Field(description="User password", min_length=1)


class RegisterRequest(BaseModel):
    email: EmailStr = Field(description="User email address")
    password: str = Field(
        description="User password",
        min_length=settings.PASSWORD_MIN_LENGTH,
    )
    username: str | None = Field(
        default=None,
        description="Optional username",
        min_length=1,
        max_length=100,
    )

    @field_validator("username")
    @classmethod
    def validate_username_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain alphanumeric characters, underscores, and hyphens")
        return v


class RefreshTokenRequest(BaseModel):
    refresh_token: str | None = Field(
        default=None,
        description=(
            "Refresh token (fallback only). "
            "Cookie-based tokens are preferred for security. "
            "This field is only used if no cookie is provided."
        ),
    )


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(description="Current password", min_length=1)
    new_password: str = Field(
        description="New password",
        min_length=settings.PASSWORD_MIN_LENGTH,
    )


class TokenResponse(BaseModel):
    access_token: str = Field(description="JWT access token")
    token_type: Literal["bearer"] = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Token expiration time in seconds")


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str | None
    is_active: bool
    is_superuser: bool
    roles: list[RoleResponse]
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None


class LoginResponse(BaseModel):
    access_token: str = Field(description="JWT access token")
    token_type: Literal["bearer"] = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Token expiration time in seconds")
    user: UserResponse = Field(description="Authenticated user information")


class RegisterResponse(BaseModel):
    user: UserResponse = Field(description="Newly registered user information")
