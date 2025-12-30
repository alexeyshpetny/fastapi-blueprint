import logging
from datetime import UTC, datetime
from typing import Final

from src.adapters.uow import SqlAlchemyUnitOfWork
from src.auth.jwt import assert_token_type, create_access_token, create_refresh_token, decode_token
from src.auth.password import get_password_hash, verify_password
from src.core.exceptions.exceptions import ConflictError, NotFoundError
from src.core.settings import settings
from src.models.user import User

logger = logging.getLogger(__name__)


class AuthService:
    _DEFAULT_ROLE_DESCRIPTION: Final[str] = "Default role assigned to newly registered users."

    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        self._uow = uow

    async def authenticate_user(self, email: str, password: str) -> User | None:
        user = await self._uow.users.get_by_email(email)
        if user is None or not user.is_active:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        user.last_login = datetime.now(UTC)
        return user

    async def create_user(self, email: str, password: str, username: str | None) -> User:
        existing = await self._uow.users.get_by_email(email)
        if existing is not None:
            raise ConflictError("Email is already registered")

        user = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=False,
        )

        default_role = await self._uow.roles.get_or_create(
            name=settings.DEFAULT_USER_ROLE,
            description=self._DEFAULT_ROLE_DESCRIPTION,
        )
        user.roles.append(default_role)

        self._uow.users.add(user)
        return user

    async def assign_role_to_user(self, user: User, role_name: str) -> None:
        role = await self._uow.roles.get_by_name(role_name)
        if role is None:
            raise NotFoundError("Role not found", details={"role": role_name})

        if role not in user.roles:
            user.roles.append(role)

    async def revoke_role_from_user(self, user: User, role_name: str) -> None:
        role = await self._uow.roles.get_by_name(role_name)
        if role is None:
            raise NotFoundError("Role not found", details={"role": role_name})

        user.roles = [r for r in user.roles if r.id != role.id]

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self._uow.users.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self._uow.users.get_by_email(email)

    async def login_user(self, email: str, password: str) -> tuple[str, str, User]:
        user = await self.authenticate_user(email, password)
        if user is None:
            raise ConflictError("Invalid email or password")

        role_names = [role.name for role in user.roles]
        access_token = create_access_token(sub=str(user.id), email=user.email, roles=role_names)
        refresh_token = create_refresh_token(sub=str(user.id))

        return access_token, refresh_token, user

    async def refresh_access_token(self, refresh_token: str) -> str:
        try:
            payload = decode_token(refresh_token)
            assert_token_type(payload, "refresh")
        except Exception as e:
            logger.warning("Invalid refresh token", extra={"error": str(e)})
            raise ConflictError("Invalid refresh token") from None

        if payload.is_expired():
            raise ConflictError("Refresh token expired")

        try:
            user_id = int(payload.sub)
        except (ValueError, TypeError):
            raise ConflictError("Invalid token payload") from None

        user = await self.get_user_by_id(user_id)
        if user is None or not user.is_active:
            raise ConflictError("User not found or inactive") from None

        role_names = [role.name for role in user.roles]
        return create_access_token(sub=str(user_id), email=user.email, roles=role_names)

    async def change_user_password(self, user: User, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.hashed_password):
            logger.warning("Failed password change attempt", extra={"user_id": user.id})
            raise ConflictError("Invalid current password") from None

        user.hashed_password = get_password_hash(new_password)
        logger.info("Password changed successfully", extra={"user_id": user.id})
