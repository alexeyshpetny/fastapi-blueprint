from src.core.exceptions.exceptions import ConflictError, UnauthorizedError


class InvalidCredentialsError(UnauthorizedError):
    """401 Unauthorized - Wrong email/password."""

    default_message: str = "Invalid email or password"


class InvalidTokenError(UnauthorizedError):
    """401 Unauthorized - Malformed or invalid JWT."""

    default_message: str = "Invalid authentication credentials"


class TokenExpiredError(UnauthorizedError):
    """401 Unauthorized - Expired JWT."""

    default_message: str = "Token expired"


class UserAlreadyExistsError(ConflictError):
    """409 Conflict - Email already registered."""

    default_message: str = "Email is already registered"
