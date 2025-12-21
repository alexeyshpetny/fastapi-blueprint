from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        x_content_type_options: str = "nosniff",
        x_frame_options: str = "DENY",
        x_xss_protection: str = "1; mode=block",
        strict_transport_security: str | None = None,
        content_security_policy: str | None = None,
        referrer_policy: str = "strict-origin-when-cross-origin",
        permissions_policy: str | None = None,
    ) -> None:
        super().__init__(app)
        self.x_content_type_options = x_content_type_options
        self.x_frame_options = x_frame_options
        self.x_xss_protection = x_xss_protection
        self.strict_transport_security = strict_transport_security
        self.content_security_policy = content_security_policy
        self.referrer_policy = referrer_policy
        self.permissions_policy = permissions_policy

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = self.x_content_type_options
        response.headers["X-Frame-Options"] = self.x_frame_options
        response.headers["X-XSS-Protection"] = self.x_xss_protection

        if self.strict_transport_security:
            response.headers["Strict-Transport-Security"] = self.strict_transport_security

        if self.content_security_policy:
            response.headers["Content-Security-Policy"] = self.content_security_policy

        response.headers["Referrer-Policy"] = self.referrer_policy

        if self.permissions_policy:
            response.headers["Permissions-Policy"] = self.permissions_policy

        return response
