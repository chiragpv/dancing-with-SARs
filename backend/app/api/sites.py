from fastapi import APIRouter

from app.schemas.site import SiteResponse
from app.services.site_service import list_sites

router = APIRouter(prefix="/api/sites", tags=["sites"])


@router.get("", response_model=list[SiteResponse])
async def get_sites() -> list[SiteResponse]:
    return [SiteResponse.model_validate(site) for site in list_sites()]
