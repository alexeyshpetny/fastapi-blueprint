from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.core.logger import request_id_context
from src.main import create_app


@pytest.fixture(autouse=True)
def clear_request_context():
    yield
    request_id_context.set(None)


@pytest.fixture
def app() -> FastAPI:
    return create_app()


@pytest.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
