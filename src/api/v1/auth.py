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
    UserResponse,
)
from src.auth.dependencies import get_current_user
from src.auth.exceptions import InvalidCredentialsError, InvalidTokenError, UserAlreadyExistsError
from src.auth.jwt import decode_token
from src.auth.token_blacklist import blacklist_token
from src.core.exceptions.exceptions import ValidationError
from src.core.settings import settings
from src.dependencies.services import get_auth_service
from src.models.user import User
from src.rate_limit import rate_limit
from src.services.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/register",
    summary="Register a new user",
    description="Register a new user account with email, password, and optional username.",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "User already exists (email or username already registered)",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Validation failed - invalid email format, password too short, or invalid username format",
        },
    },
)
@rate_limit("5/minute")
async def register(
    request: Request,
    response: Response,
    data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> RegisterResponse:
    try:
        await auth_service.create_user(
            email=data.email,
            password=data.password,
            username=data.username,
        )
        user = await auth_service.get_user_by_email(data.email)
        return RegisterResponse(user=UserResponse.model_validate(user))
    except UserAlreadyExistsError:
        logger.warning("Registration attempt with existing email", extra={"email": data.email})
        raise ValidationError(
            message="Unable to complete registration. Please check your information and try again."
        ) from None


@router.post(
    "/login",
    summary="Login with email and password",
    description="Authenticate a user and receive an access token. Refresh token is set in HTTP-only cookie.",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid credentials - wrong email/password or user account is inactive",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Validation failed - missing username or password fields",
        },
    },
)
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
    except InvalidCredentialsError:
        logger.warning("Failed login attempt", extra={"email": form_data.username})
        raise


@router.post(
    "/refresh",
    summary="Refresh access token",
    description="Get a new access token using a refresh token (from cookie or request body).",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": (
                "Invalid refresh token - token not provided, malformed, wrong type, expired, "
                "blacklisted, user not found, or user account is inactive"
            ),
        },
    },
)
@rate_limit("10/minute")
async def refresh(
    request: Request,
    response: Response,
    refresh_token_request: RefreshTokenRequest | None = None,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    token = request.cookies.get(settings.JWT_REFRESH_TOKEN_COOKIE_NAME)

    if not token:
        if refresh_token_request and refresh_token_request.refresh_token:
            token = refresh_token_request.refresh_token
            logger.warning(
                "Refresh token provided in request body instead of cookie",
                extra={
                    "token_source": "body",
                    "security_note": "Cookie-based tokens are more secure (HTTP-only)",
                },
            )
        else:
            raise InvalidTokenError("Refresh token not provided")

    access_token, new_refresh_token = await auth_service.refresh_access_token(token)

    response.set_cookie(
        key=settings.JWT_REFRESH_TOKEN_COOKIE_NAME,
        value=new_refresh_token,
        httponly=settings.JWT_REFRESH_TOKEN_HTTP_ONLY,
        secure=settings.JWT_REFRESH_TOKEN_SECURE,
        samesite=settings.JWT_REFRESH_TOKEN_SAME_SITE,
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_SECONDS,
    )

    payload = decode_token(access_token)
    user_id = int(payload.sub)
    user = await auth_service.get_user_by_id(user_id)
    if user is None:
        raise InvalidTokenError("User not found")

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_SECONDS,
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/logout",
    summary="Logout user",
    description=(
        "Invalidate refresh token and clear authentication cookies. "
        "Always returns 200 even if no token is present or token is invalid."
    ),
    status_code=status.HTTP_200_OK,
)
@rate_limit("20/minute")
async def logout(request: Request, response: Response) -> dict[str, str]:
    if refresh_token := request.cookies.get(settings.JWT_REFRESH_TOKEN_COOKIE_NAME):
        try:
            payload = decode_token(refresh_token, verify_exp=False)
            if payload.jti:
                expires_at = payload.expires_at()
                await blacklist_token(payload.jti, expires_at)
                logger.info("Refresh token blacklisted on logout", extra={"jti": payload.jti})
        except Exception as e:
            logger.warning("Failed to blacklist token on logout", extra={"error": str(e)})

    response.delete_cookie(
        key=settings.JWT_REFRESH_TOKEN_COOKIE_NAME,
        httponly=settings.JWT_REFRESH_TOKEN_HTTP_ONLY,
        secure=settings.JWT_REFRESH_TOKEN_SECURE,
        samesite=settings.JWT_REFRESH_TOKEN_SAME_SITE,
    )
    return {"message": "Logged out successfully"}


@router.get(
    "/me",
    summary="Get current user information",
    description="Get the authenticated user's profile information.",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": ("Authentication required - token missing, expired, invalid, revoked, or user not found"),
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "User account is inactive",
        },
    },
)
@rate_limit("60/minute")
async def get_current_user_info(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.post(
    "/change-password",
    summary="Change user password",
    description="Change the authenticated user's password. Requires current password verification.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": ("Invalid current password, token missing, expired, invalid, revoked, or user not found"),
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "User account is inactive",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Validation failed - new password too short or missing required fields",
        },
    },
)
@rate_limit("5/minute")
async def change_password(
    request: Request,
    data: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    await auth_service.change_user_password(current_user, data.current_password, data.new_password)
    return {"message": "Password changed successfully"}
