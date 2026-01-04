class ApplicationError(Exception):
    """Base application error with configurable status code and message."""

    status_code: int = 500
    default_message: str = "An error occurred"

    def __init__(
        self,
        message: str | None = None,
        status_code: int | None = None,
        details: dict | list | str | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.status_code = status_code or type(self).status_code
        self.details = details
        super().__init__(self.message)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"status_code={self.status_code}, "
            f"message={self.message!r}, "
            f"details={self.details!r})"
        )

    def __str__(self) -> str:
        return self.message


class ValidationError(ApplicationError):
    """400 Bad Request - Validation failed."""

    status_code: int = 400
    default_message: str = "Validation failed"


class UnauthorizedError(ApplicationError):
    """401 Unauthorized - Authentication required."""

    status_code: int = 401
    default_message: str = "Unauthorized"


class ForbiddenError(ApplicationError):
    """403 Forbidden - Access denied."""

    status_code: int = 403
    default_message: str = "Forbidden"


class NotFoundError(ApplicationError):
    """404 Not Found - Resource not found."""

    status_code: int = 404
    default_message: str = "Resource not found"


class ConflictError(ApplicationError):
    """409 Conflict - Resource conflict."""

    status_code: int = 409
    default_message: str = "Conflict occurred"


class InternalServerError(ApplicationError):
    """500 Internal Server Error - Server error."""

    status_code: int = 500
    default_message: str = "Internal server error"


class ServiceUnavailableError(ApplicationError):
    """503 Service Unavailable - Service temporarily unavailable."""

    status_code: int = 503
    default_message: str = "Service temporarily unavailable"
