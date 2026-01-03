from src.core.exceptions.exceptions import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError


class InvalidCredentialsError(UnauthorizedError):
    """401 Unauthorized - Wrong email/password."""

    default_message: str = "Invalid email or password"


class InvalidTokenError(UnauthorizedError):
    """401 Unauthorized - Malformed or invalid JWT."""

    default_message: str = "Invalid authentication credentials"


class TokenExpiredError(UnauthorizedError):
    """401 Unauthorized - Expired JWT."""

    default_message: str = "Token expired"


class InactiveUserError(ForbiddenError):
    """403 Forbidden - User account is disabled."""

    default_message: str = "User is inactive"


class InsufficientPermissionsError(ForbiddenError):
    """403 Forbidden - Missing required role."""

    default_message: str = "Insufficient permissions"


class UserNotFoundError(NotFoundError):
    """404 Not Found - User doesn't exist."""

    default_message: str = "User not found"


class UserAlreadyExistsError(ConflictError):
    """409 Conflict - Email already registered."""

    default_message: str = "Email is already registered"
