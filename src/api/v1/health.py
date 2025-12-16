import logging

from fastapi import APIRouter

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check() -> dict[str, str]:
    logger.debug("Health check requested")
    return {"status": "ok"}
