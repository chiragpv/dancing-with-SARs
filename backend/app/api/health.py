from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    dependencies: dict[str, Literal["ok", "degraded", "unavailable", "not_configured"]] = Field(
        default_factory=dict
    )


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
