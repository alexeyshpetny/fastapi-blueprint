from fastapi import status
from httpx import AsyncClient

from src.core.settings import settings


async def test_check_liveness(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/live")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "alive"
    assert data["service"] == settings.SERVICE_NAME
    assert "version" in data


async def test_check_readiness_success(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ready"
    assert data["service"] == settings.SERVICE_NAME
    assert "version" in data
    assert "checks" in data
    assert data["checks"]["database"] == "ok"
