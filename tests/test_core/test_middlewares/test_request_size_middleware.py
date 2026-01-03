import pytest
from fastapi import FastAPI, Request, Response, status
from httpx import AsyncClient

from src.core.settings import settings


@pytest.mark.unit
async def test_request_size_limit_enforced(app: FastAPI, client: AsyncClient) -> None:
    @app.post("/test-large-body")
    async def _(request: Request, response: Response):
        return {"message": "success"}

    response = await client.post(
        "/test-large-body",
        headers={"Content-Length": str(settings.MAX_REQUEST_BODY_SIZE + 1)},
        json={"data": "test"},
    )

    assert response.status_code == status.HTTP_413_CONTENT_TOO_LARGE
    data = response.json()
    assert data["error"] == "Request entity too large"
    assert data["max_size"] == settings.MAX_REQUEST_BODY_SIZE


@pytest.mark.unit
@pytest.mark.parametrize(
    ("content_length", "path_suffix"),
    [
        (settings.MAX_REQUEST_BODY_SIZE - 1, "valid"),
        (settings.MAX_REQUEST_BODY_SIZE, "exact"),
        (None, "no-header"),
    ],
)
async def test_request_size_limit_allows_valid_requests(
    app: FastAPI,
    client: AsyncClient,
    content_length: int | None,
    path_suffix: str,
) -> None:
    path = f"/test-{path_suffix}"

    @app.post(path)
    async def _(request: Request, response: Response):
        return {"message": "success"}

    headers = {"Content-Length": str(content_length)} if content_length else {}
    response = await client.post(path, headers=headers, json={"data": "test"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "success"
