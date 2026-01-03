import logging
from datetime import UTC, datetime
from typing import Final

from src.adapters.role_repository import SqlAlchemyRoleRepository
from src.adapters.user_repository import SqlAlchemyUserRepository
from src.auth.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    UserAlreadyExistsError,
)
from src.auth.jwt import assert_token_type, create_access_token, create_refresh_token, decode_token
from src.auth.password import get_password_hash, verify_password
from src.auth.token_blacklist import blacklist_token, is_token_blacklisted
from src.core.settings import settings
from src.models.user import User

logger = logging.getLogger(__name__)


class AuthService:
    _DEFAULT_ROLE_DESCRIPTION: Final[str] = "Default role assigned to newly registered users."

    def __init__(
        self,
        users: SqlAlchemyUserRepository,
        roles: SqlAlchemyRoleRepository,
    ) -> None:
        self._users = users
        self._roles = roles

    async def authenticate_user(self, email: str, password: str) -> User | None:
        user = await self._users.get_by_email(email)
        if user is None or not user.is_active:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        user.last_login = datetime.now(UTC)
        return user

    async def create_user(self, email: str, password: str, username: str | None) -> User:
        existing = await self._users.get_by_email(email)
        if existing is not None:
            raise UserAlreadyExistsError()

        user = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=False,
        )

        default_role = await self._roles.get_or_create(
            name=settings.DEFAULT_USER_ROLE,
            description=self._DEFAULT_ROLE_DESCRIPTION,
        )
        user.roles.append(default_role)

        self._users.add(user)
        await self._users.flush()
        return user

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self._users.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self._users.get_by_email(email)

    async def login_user(self, email: str, password: str) -> tuple[str, str, User]:
        user = await self.authenticate_user(email, password)
        if user is None:
            raise InvalidCredentialsError()

        role_names = [role.name for role in user.roles]
        access_token = create_access_token(sub=str(user.id), email=user.email, roles=role_names)
        refresh_token = create_refresh_token(sub=str(user.id))
        return access_token, refresh_token, user

    async def refresh_access_token(self, refresh_token: str) -> tuple[str, str]:
        try:
            payload = decode_token(refresh_token)
            assert_token_type(payload, "refresh")
        except Exception as e:
            logger.warning("Invalid refresh token", extra={"error": str(e)})
            raise InvalidTokenError() from e

        if payload.is_expired():
            raise TokenExpiredError()

        if payload.jti and await is_token_blacklisted(payload.jti):
            logger.warning("Attempted use of blacklisted refresh token", extra={"jti": payload.jti})
            raise InvalidTokenError("Token has been revoked")

        try:
            user_id = int(payload.sub)
        except (ValueError, TypeError) as e:
            raise InvalidTokenError() from e

        user = await self.get_user_by_id(user_id)
        if user is None or not user.is_active:
            raise InvalidTokenError()

        if payload.jti:
            expires_at = payload.expires_at()
            await blacklist_token(payload.jti, expires_at)

        # Create new tokens
        role_names = [role.name for role in user.roles]
        new_access_token = create_access_token(sub=str(user_id), email=user.email, roles=role_names)
        new_refresh_token = create_refresh_token(sub=str(user_id))

        logger.info("Tokens refreshed and rotated", extra={"user_id": user_id})
        return new_access_token, new_refresh_token

    async def change_user_password(self, user: User, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.hashed_password):
            logger.warning("Failed password change attempt", extra={"user_id": user.id})
            raise InvalidCredentialsError("Invalid current password")

        user.hashed_password = get_password_hash(new_password)
        logger.info("Password changed successfully", extra={"user_id": user.id})
