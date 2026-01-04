import logging

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.v1.schemas.health import LivenessResponse, ReadinessResponse
from src.dependencies.services import get_health_service
from src.services.health_service import HealthService

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get(
    "/health/live",
    summary="Liveness check",
    description=(
        "Liveness check endpoint. Returns 200 if the application process is running. "
        "This endpoint does not check external dependencies."
    ),
    response_model=LivenessResponse,
    status_code=status.HTTP_200_OK,
)
async def check_liveness(
    health_service: HealthService = Depends(get_health_service),
) -> LivenessResponse:
    logger.debug("Liveness check requested")
    result = await health_service.check_liveness()
    return LivenessResponse(**result)


@router.get(
    "/health/ready",
    summary="Readiness check",
    description=(
        "Readiness check endpoint. Returns 200 if the service is ready to accept traffic. "
        "Returns 503 if the service is not ready."
    ),
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Service is not ready",
            "content": {
                "application/json": {
                    "example": {
                        "status": "not_ready",
                        "service": "fastapi-blueprint",
                        "version": "1.0.0",
                        "checks": {"database": "error", "cache": "error"},
                        "error": "Database connection failed; Cache connection failed",
                    }
                }
            },
        },
    },
)
async def check_readiness(
    health_service: HealthService = Depends(get_health_service),
) -> ReadinessResponse:
    logger.debug("Readiness check requested")
    result = await health_service.check_readiness()
    response = ReadinessResponse(**result)

    if result["status"] == "not_ready":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response.model_dump(),
        )

    return response
