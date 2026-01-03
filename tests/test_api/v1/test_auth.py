import pytest
from fastapi import status
from httpx import AsyncClient

from src.auth.jwt import decode_token
from src.core.settings import settings


@pytest.mark.integration
class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "username": "newuser",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["username"] == "newuser"
        assert data["user"]["is_active"] is True
        assert data["user"]["is_superuser"] is False
        assert len(data["user"]["roles"]) == 1
        assert data["user"]["roles"][0]["name"] == settings.DEFAULT_USER_ROLE

    async def test_register_duplicate_email(self, client: AsyncClient, user_factory):
        await user_factory(email="existing@example.com", password="Password123!")

        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "existing@example.com",
                "password": "AnotherPassword123!",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        error_message = data.get("error", data.get("detail", ""))
        assert "Unable to complete registration" in error_message
        assert "Email is already registered" not in error_message

    async def test_register_invalid_email(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_register_short_password(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "short",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_register_invalid_username(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "SecurePass123!",
                "username": "invalid username!",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.integration
class TestLogin:
    async def test_login_success(self, client: AsyncClient, user_factory):
        await user_factory(email="test@example.com", password="TestPassword123!")

        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "TestPassword123!",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == settings.JWT_ACCESS_TOKEN_EXPIRE_SECONDS
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"

        assert settings.JWT_REFRESH_TOKEN_COOKIE_NAME in response.cookies
        payload = decode_token(data["access_token"])
        assert payload.type == "access"
        assert payload.email == "test@example.com"

    async def test_login_invalid_credentials(self, client: AsyncClient, user_factory):
        await user_factory(email="test@example.com", password="CorrectPassword123!")

        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Invalid email or password" in data.get("error", data.get("detail", ""))

    async def test_login_nonexistent_user(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "SomePassword123!",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_inactive_user(self, client: AsyncClient, user_factory):
        await user_factory(email="inactive@example.com", password="Password123!", is_active=False)

        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "inactive@example.com",
                "password": "Password123!",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
class TestRefresh:
    async def test_refresh_success(self, client: AsyncClient, user_factory):
        await user_factory(email="test@example.com", password="Password123!")

        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "Password123!",
            },
        )
        assert login_response.status_code == status.HTTP_200_OK

        refresh_token = login_response.cookies.get(settings.JWT_REFRESH_TOKEN_COOKIE_NAME)
        assert refresh_token is not None

        client.cookies.set(settings.JWT_REFRESH_TOKEN_COOKIE_NAME, refresh_token)
        refresh_response = await client.post("/api/v1/auth/refresh")

        assert refresh_response.status_code == status.HTTP_200_OK
        data = refresh_response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == settings.JWT_ACCESS_TOKEN_EXPIRE_SECONDS

        payload = decode_token(data["access_token"])
        assert payload.type == "access"
        assert payload.email == "test@example.com"

    async def test_refresh_with_body_token(self, client: AsyncClient, user_factory):
        await user_factory(email="test@example.com", password="Password123!")

        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "Password123!",
            },
        )
        refresh_token = login_response.cookies.get(settings.JWT_REFRESH_TOKEN_COOKIE_NAME)

        refresh_response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert refresh_response.status_code == status.HTTP_200_OK
        assert "access_token" in refresh_response.json()

    async def test_refresh_no_token(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/refresh")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Refresh token not provided" in data.get("error", data.get("detail", ""))

    async def test_refresh_invalid_token(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
class TestLogout:
    async def test_logout_success(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/logout")

        assert response.status_code == status.HTTP_200_OK
        assert "Logged out successfully" in response.json()["message"]

        cookies = response.cookies
        cookie_value = cookies.get(settings.JWT_REFRESH_TOKEN_COOKIE_NAME)
        assert cookie_value is None or cookie_value == "" or "max-age=0" in str(cookies)


@pytest.mark.integration
class TestMe:
    async def test_me_success(self, client: AsyncClient, user_factory):
        user = await user_factory(email="test@example.com", password="Password123!")

        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "Password123!",
            },
        )
        access_token = login_response.json()["access_token"]

        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert me_response.status_code == status.HTTP_200_OK
        data = me_response.json()
        assert data["email"] == "test@example.com"
        assert data["id"] == user.id

    async def test_me_no_token(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_me_invalid_token(self, client: AsyncClient):
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_me_inactive_user(self, client: AsyncClient, user_factory):
        await user_factory(email="inactive@example.com", password="Password123!", is_active=False)

        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "inactive@example.com",
                "password": "Password123!",
            },
        )
        assert login_response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
class TestChangePassword:
    async def test_change_password_success(self, client: AsyncClient, user_factory):
        await user_factory(email="test@example.com", password="OldPassword123!")

        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "OldPassword123!",
            },
        )
        access_token = login_response.json()["access_token"]

        change_response = await client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "current_password": "OldPassword123!",
                "new_password": "NewPassword123!",
            },
        )

        assert change_response.status_code == status.HTTP_200_OK
        assert "Password changed successfully" in change_response.json()["message"]

        old_login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "OldPassword123!",
            },
        )
        assert old_login_response.status_code == status.HTTP_401_UNAUTHORIZED

        new_login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "NewPassword123!",
            },
        )
        assert new_login_response.status_code == status.HTTP_200_OK

    async def test_change_password_wrong_current(self, client: AsyncClient, user_factory):
        await user_factory(email="test@example.com", password="CorrectPassword123!")

        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "CorrectPassword123!",
            },
        )
        access_token = login_response.json()["access_token"]

        change_response = await client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "current_password": "WrongPassword123!",
                "new_password": "NewPassword123!",
            },
        )

        assert change_response.status_code == status.HTTP_401_UNAUTHORIZED
        data = change_response.json()
        assert "Invalid current password" in data.get("error", data.get("detail", ""))

    async def test_change_password_short_new(self, client: AsyncClient, user_factory):
        await user_factory(email="test@example.com", password="Password123!")

        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "Password123!",
            },
        )
        access_token = login_response.json()["access_token"]

        change_response = await client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "current_password": "Password123!",
                "new_password": "short",
            },
        )
        assert change_response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_change_password_no_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "OldPassword123!",
                "new_password": "NewPassword123!",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
