import pytest

from src.auth.password import get_password_hash, validate_password, verify_password
from src.core.settings import settings


def test_validate_password_min_length() -> None:
    with pytest.raises(ValueError, match="Password must be at least"):
        validate_password("x" * (settings.PASSWORD_MIN_LENGTH - 1))

    validate_password("x" * settings.PASSWORD_MIN_LENGTH)


def test_validate_password_max_72_bytes() -> None:
    with pytest.raises(ValueError, match="Password must be at most 72 bytes"):
        validate_password("x" * 73)


def test_password_hash_and_verify_roundtrip() -> None:
    password = "x" * settings.PASSWORD_MIN_LENGTH
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_verify_password_invalid_hash_returns_false() -> None:
    assert verify_password("any", "not-a-valid-hash") is False
