from fastapi import APIRouter
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str


router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="customer-service-agent",
    )
