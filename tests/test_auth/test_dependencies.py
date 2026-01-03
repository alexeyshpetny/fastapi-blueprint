from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException, status
from jose import jwt

from src.auth.dependencies import (
    get_current_user,
    require_all_roles,
    require_any_role,
    require_role,
)
from src.auth.jwt import create_access_token, create_refresh_token
from src.core.settings import settings
from src.services.auth_service import AuthService


@pytest.mark.integration
class TestGetCurrentUser:
    async def test_get_current_user_success(self, auth_service: AuthService, user_factory, session):
        user = await user_factory(email="test@example.com", password="password123")
        await session.commit()

        token = create_access_token(sub=str(user.id), email=user.email)
        result = await get_current_user(token=token, auth_service=auth_service)

        assert result.id == user.id
        assert result.email == "test@example.com"

    async def test_get_current_user_no_token(self, auth_service: AuthService):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=None, auth_service=auth_service)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in exc_info.value.detail

    async def test_get_current_user_invalid_token(self, auth_service: AuthService):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token="invalid_token", auth_service=auth_service)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid authentication credentials" in exc_info.value.detail

    async def test_get_current_user_expired_token(self, auth_service: AuthService):
        expired_payload = {
            "sub": "1",
            "type": "access",
            "iat": int((datetime.now(UTC) - timedelta(hours=2)).timestamp()),
            "exp": int((datetime.now(UTC) - timedelta(hours=1)).timestamp()),
            "email": "test@example.com",
        }
        expired_token = jwt.encode(expired_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=expired_token, auth_service=auth_service)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Token expired" in exc_info.value.detail

    async def test_get_current_user_wrong_token_type(self, auth_service: AuthService, user_factory):
        user = await user_factory(email="test@example.com", password="password123")
        refresh_token = create_refresh_token(sub=str(user.id))

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=refresh_token, auth_service=auth_service)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_current_user_not_found(self, auth_service: AuthService):
        token = create_access_token(sub="999", email="nonexistent@example.com")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, auth_service=auth_service)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "User not found" in exc_info.value.detail

    async def test_get_current_user_inactive(self, auth_service: AuthService, user_factory, session):
        user = await user_factory(email="test@example.com", password="password123", is_active=False)
        await session.commit()

        token = create_access_token(sub=str(user.id), email=user.email)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, auth_service=auth_service)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "User is inactive" in exc_info.value.detail


async def _call_checker(checker, user):
    return await checker(**{"current_user": user})


@pytest.mark.integration
class TestRequireRole:
    async def test_require_role_success(self, user_factory, session):
        user = await user_factory(email="test@example.com", password="password123", roles=["admin"])
        await session.commit()

        result = await _call_checker(require_role("admin"), user)

        assert result.id == user.id

    async def test_require_role_missing(self, user_factory):
        user = await user_factory(email="test@example.com", password="password123")

        with pytest.raises(HTTPException) as exc_info:
            await _call_checker(require_role("admin"), user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Insufficient permissions" in exc_info.value.detail
        assert "admin" in exc_info.value.detail


@pytest.mark.integration
class TestRequireAnyRole:
    async def test_require_any_role_success(self, user_factory, session):
        user = await user_factory(email="test@example.com", password="password123", roles=["moderator"])
        await session.commit()

        result = await _call_checker(require_any_role("moderator", "admin"), user)

        assert result.id == user.id

    async def test_require_any_role_missing(self, user_factory):
        user = await user_factory(email="test@example.com", password="password123")

        with pytest.raises(HTTPException) as exc_info:
            await _call_checker(require_any_role("moderator", "admin"), user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Insufficient permissions" in exc_info.value.detail


@pytest.mark.integration
class TestRequireAllRoles:
    async def test_require_all_roles_success(self, user_factory, session):
        user = await user_factory(email="test@example.com", password="password123", roles=["admin", "moderator"])
        await session.commit()

        result = await _call_checker(require_all_roles("admin", "moderator"), user)

        assert result.id == user.id

    async def test_require_all_roles_missing_one(self, user_factory):
        user = await user_factory(email="test@example.com", password="password123", roles=["admin"])

        with pytest.raises(HTTPException) as exc_info:
            await _call_checker(require_all_roles("admin", "moderator"), user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Insufficient permissions" in exc_info.value.detail
        assert "moderator" in exc_info.value.detail
