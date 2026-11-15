from pydantic import BaseModel, ConfigDict, Field

from app.models.site import SiteKey


class SiteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: SiteKey
    name: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    description: str
