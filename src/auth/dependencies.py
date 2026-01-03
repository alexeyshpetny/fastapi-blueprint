from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from src.auth.jwt import assert_token_type, decode_token
from src.auth.token_blacklist import is_token_blacklisted
from src.core.settings import settings
from src.dependencies.services import get_auth_service
from src.models.user import User
from src.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False,
)

_AUTH_HEADERS = {"WWW-Authenticate": "Bearer"}


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers=_AUTH_HEADERS,
    )


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    if not token:
        raise _unauthorized("Not authenticated")

    try:
        payload = decode_token(token)
        assert_token_type(payload, "access")
    except JWTError as e:
        error_str = str(e).lower()
        if "expired" in error_str or "exp" in error_str:
            raise _unauthorized("Token expired") from e
        raise _unauthorized("Invalid authentication credentials") from e

    if payload.jti and await is_token_blacklisted(payload.jti):
        raise _unauthorized("Token has been revoked")

    try:
        user_id = int(payload.sub)
    except (ValueError, TypeError) as e:
        raise _unauthorized("Invalid token payload") from e

    user = await auth_service.get_user_by_id(user_id)
    if user is None:
        raise _unauthorized("User not found")

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )

    return user


def require_role(role_name: str) -> Callable[[User], Awaitable[User]]:
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if role_name not in {role.name for role in current_user.roles}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: requires role '{role_name}'",
            )
        return current_user

    return role_checker


def require_any_role(*role_names: str) -> Callable[[User], Awaitable[User]]:
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        user_roles = {role.name for role in current_user.roles}
        if not any(r in user_roles for r in role_names):
            roles_str = ", ".join(f"'{r}'" for r in role_names)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: requires one of roles {roles_str}",
            )
        return current_user

    return role_checker


def require_all_roles(*role_names: str) -> Callable[[User], Awaitable[User]]:
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        user_roles = {role.name for role in current_user.roles}
        missing = set(role_names) - user_roles
        if missing:
            roles_str = ", ".join(f"'{r}'" for r in missing)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: missing roles {roles_str}",
            )
        return current_user

    return role_checker
