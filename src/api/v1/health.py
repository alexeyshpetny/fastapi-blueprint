import logging

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.v1.schemas.health import LivenessResponse, ReadinessResponse
from src.dependencies.services import get_health_service
from src.services.health_service import HealthService

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get(
    "/health/live",
    summary="Liveness probe",
    description=(
        "Kubernetes liveness probe endpoint. Returns 200 if the application process is running. "
        "This endpoint does not check external dependencies."
    ),
    response_model=LivenessResponse,
    status_code=status.HTTP_200_OK,
)
async def liveness_probe(
    health_service: HealthService = Depends(get_health_service),
) -> LivenessResponse:
    logger.debug("Liveness probe requested")
    result = await health_service.check_liveness()
    return LivenessResponse(**result)


@router.get(
    "/health/ready",
    summary="Readiness probe",
    description=(
        "Kubernetes readiness probe endpoint. Returns 200 if the service is ready to accept traffic "
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
                        "service": "shpetny-fastapi-blueprint",
                        "version": "1.0.0",
                        "checks": {"database": "error", "cache": "error"},
                        "error": "Database connection failed; Cache connection failed",
                    }
                }
            },
        },
    },
)
async def readiness_probe(
    health_service: HealthService = Depends(get_health_service),
) -> ReadinessResponse:
    logger.debug("Readiness probe requested")
    result = await health_service.check_readiness()
    response = ReadinessResponse(**result)

    if result["status"] == "not_ready":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response.model_dump(),
        )

    return response
