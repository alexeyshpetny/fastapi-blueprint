from pydantic import BaseModel, Field


class LivenessResponse(BaseModel):
    status: str = Field(..., description="Liveness status", examples=["alive"])
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")


class ReadinessResponse(BaseModel):
    status: str = Field(..., description="Readiness status", examples=["ready", "not_ready"])
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    checks: dict[str, str] = Field(..., description="Readiness check results")
    error: str | None = Field(None, description="Error message if not ready")
