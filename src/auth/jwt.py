from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from src.auth.schemas import TokenPayload, TokenType
from src.core.settings import settings


def _to_unix_seconds(dt: datetime) -> int:
    return int(dt.timestamp())


def create_access_token(*, sub: str, email: str | None = None, roles: list[str] | None = None) -> str:
    issued_at = datetime.now(UTC)
    expires_at = issued_at + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = TokenPayload(
        sub=sub,
        type="access",
        iat=_to_unix_seconds(issued_at),
        exp=_to_unix_seconds(expires_at),
        email=email,
        roles=roles or [],
    ).model_dump()
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(*, sub: str) -> str:
    issued_at = datetime.now(UTC)
    expires_at = issued_at + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    payload = TokenPayload(
        sub=sub,
        type="refresh",
        iat=_to_unix_seconds(issued_at),
        exp=_to_unix_seconds(expires_at),
    ).model_dump()
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    return TokenPayload.model_validate(decoded)


def assert_token_type(payload: TokenPayload, expected: TokenType) -> None:
    if payload.type != expected:
        raise JWTError(f"Invalid token type: expected={expected}, got={payload.type}")
