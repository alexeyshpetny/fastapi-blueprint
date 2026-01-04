import pytest
from fastapi import status
from httpx import AsyncClient

from src.core.settings import settings


@pytest.mark.unit
async def test_check_liveness(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/liveness")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "alive"
    assert data["service"] == settings.SERVICE_NAME
    assert "version" in data


@pytest.mark.integration
async def test_check_readiness_success(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/readiness")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ready"
    assert data["service"] == settings.SERVICE_NAME
    assert "version" in data
    assert "checks" in data
    assert data["checks"]["database"] == "ok"
