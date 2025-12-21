import pytest
from httpx import AsyncClient

from src.core.settings import settings


@pytest.mark.unit
async def test_security_headers_core(client: AsyncClient) -> None:
    if not settings.SECURITY_HEADERS_ENABLED:
        pytest.skip("Security headers are disabled")

    response = await client.get("/api/v1/health/live")

    assert response.headers["X-Content-Type-Options"] == settings.SECURITY_X_CONTENT_TYPE_OPTIONS
    assert response.headers["X-Frame-Options"] == settings.SECURITY_X_FRAME_OPTIONS
    assert response.headers["X-XSS-Protection"] == settings.SECURITY_X_XSS_PROTECTION
    assert response.headers["Referrer-Policy"] == settings.SECURITY_REFERRER_POLICY


@pytest.mark.unit
async def test_security_headers_conditional(client: AsyncClient) -> None:
    if not settings.SECURITY_HEADERS_ENABLED:
        pytest.skip("Security headers are disabled")

    response = await client.get("/api/v1/health/live")

    if settings.SECURITY_STRICT_TRANSPORT_SECURITY:
        assert response.headers["Strict-Transport-Security"] == settings.SECURITY_STRICT_TRANSPORT_SECURITY
    else:
        assert "Strict-Transport-Security" not in response.headers

    if settings.SECURITY_CONTENT_SECURITY_POLICY:
        assert response.headers["Content-Security-Policy"] == settings.SECURITY_CONTENT_SECURITY_POLICY
    else:
        assert "Content-Security-Policy" not in response.headers

    if settings.SECURITY_PERMISSIONS_POLICY:
        assert response.headers["Permissions-Policy"] == settings.SECURITY_PERMISSIONS_POLICY
    else:
        assert "Permissions-Policy" not in response.headers
