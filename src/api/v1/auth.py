import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from src.api.v1.schemas.auth import (
    ChangePasswordRequest,
    LoginResponse,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserResponse,
)
from src.auth.dependencies import get_current_user
from src.core.exceptions.exceptions import ConflictError
from src.core.settings import settings
from src.dependencies.services import get_auth_service
from src.models.user import User
from src.rate_limit import rate_limit
from src.services.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
@rate_limit("5/minute")
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> RegisterResponse:
    try:
        await auth_service.create_user(
            email=request.email,
            password=request.password,
            username=request.username,
        )
        user = await auth_service.get_user_by_email(request.email)
        return RegisterResponse(user=UserResponse.model_validate(user))
    except ConflictError:
        logger.warning("Registration attempt with existing email", extra={"email": request.email})
        raise ConflictError("Registration failed") from None


@router.post("/login", response_model=LoginResponse)
@rate_limit("5/minute")
async def login(
    request: Request,
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    try:
        access_token, refresh_token, user = await auth_service.login_user(
            form_data.username,
            form_data.password,
        )
        response.set_cookie(
            key=settings.JWT_REFRESH_TOKEN_COOKIE_NAME,
            value=refresh_token,
            httponly=settings.JWT_REFRESH_TOKEN_HTTP_ONLY,
            secure=settings.JWT_REFRESH_TOKEN_SECURE,
            samesite=settings.JWT_REFRESH_TOKEN_SAME_SITE,
            max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_SECONDS,
        )
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_SECONDS,
            user=UserResponse.model_validate(user),
        )
    except ConflictError:
        logger.warning("Failed login attempt", extra={"email": form_data.username})
        raise


@router.post("/refresh", response_model=TokenResponse)
@rate_limit("10/minute")
async def refresh(
    request: Request,
    refresh_token_request: RefreshTokenRequest | None = None,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    token = request.cookies.get(settings.JWT_REFRESH_TOKEN_COOKIE_NAME)
    if not token and refresh_token_request:
        token = refresh_token_request.refresh_token

    if not token:
        raise ConflictError("Refresh token not provided")

    access_token = await auth_service.refresh_access_token(token)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_SECONDS,
    )


@router.post("/logout")
@rate_limit("20/minute")
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(
        key=settings.JWT_REFRESH_TOKEN_COOKIE_NAME,
        httponly=settings.JWT_REFRESH_TOKEN_HTTP_ONLY,
        secure=settings.JWT_REFRESH_TOKEN_SECURE,
        samesite=settings.JWT_REFRESH_TOKEN_SAME_SITE,
    )
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
@rate_limit("60/minute")
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.post("/change-password")
@rate_limit("5/minute")
async def change_password(
    request: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    await auth_service.change_user_password(current_user, request.current_password, request.new_password)
    return {"message": "Password changed successfully"}
