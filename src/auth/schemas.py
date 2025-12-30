from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

TokenType = Literal["access", "refresh"]


class TokenPayload(BaseModel):
    """Validated JWT payload we expect to encode/decode."""

    sub: str = Field(description="Subject (user identifier)")
    type: TokenType = Field(description="Token type")
    exp: int = Field(description="Expiration timestamp (unix seconds)")
    iat: int = Field(description="Issued-at timestamp (unix seconds)")

    email: str | None = None
    roles: list[str] = Field(default_factory=list)

    @field_validator("roles")
    @classmethod
    def normalize_roles(cls, v: list[str]) -> list[str]:
        return sorted({r for r in v if r})

    def is_expired(self, *, now: datetime | None = None) -> bool:
        now_ts = int((now or datetime.now(UTC)).timestamp())
        return now_ts >= self.exp
