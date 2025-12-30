from datetime import datetime, timedelta, timezone

import pytest
from jose import JWTError, jwt

from src.auth.jwt import create_access_token, create_refresh_token, decode_token
from src.core.settings import settings


def test_create_and_decode_access_token() -> None:
    token = create_access_token(sub="123", email="a@b.com", roles=["admin", "user", "admin"])
    payload = decode_token(token)

    assert payload.sub == "123"
    assert payload.type == "access"
    assert payload.email == "a@b.com"
    assert payload.roles == ["admin", "user"]
    assert payload.exp > payload.iat


def test_create_and_decode_refresh_token() -> None:
    token = create_refresh_token(sub="123")
    payload = decode_token(token)

    assert payload.sub == "123"
    assert payload.type == "refresh"
    assert payload.email is None


def test_decode_expired_token_raises() -> None:
    now = datetime.now(timezone.utc)
    expired_payload = {
        "sub": "123",
        "type": "access",
        "iat": int((now - timedelta(hours=2)).timestamp()),
        "exp": int((now - timedelta(hours=1)).timestamp()),
    }
    token = jwt.encode(expired_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    with pytest.raises(JWTError):
        decode_token(token)


