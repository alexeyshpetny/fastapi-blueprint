from fastapi import APIRouter

from src.api.v1 import auth, health, protected
from src.core.settings import settings

router = APIRouter(prefix=settings.API_V1_PREFIX)
router.include_router(health.router)
router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(protected.router, prefix="/protected", tags=["protected"])
