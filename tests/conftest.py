from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from src.core.logger import request_id_context
from src.main import app


@pytest.fixture(autouse=True)
def clear_request_context():
    yield
    request_id_context.set(None)


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
