from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ObservationRecordResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    site: str | None = None
    year: int | None = None
    source_file: str | None = None
    source_sheet: str | None = None
    source_row: int | None = None
    acquisition_time: datetime | str | None = None
    satellite: str | None = None
    band: str | None = None
    polarisation: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    backscatter_db: float | None = None
    coherence: float | None = None
    rainfall: float | None = None
    soil_moisture: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ObservationListResponse(BaseModel):
    dataset_status: Literal["loaded", "unavailable", "invalid", "missing"]
    source_file: str | None = None
    dataset_path: str | None = None
    message: str
    count: int
    observations: list[ObservationRecordResponse] = Field(default_factory=list)


class ObservationSummaryResponse(BaseModel):
    dataset_status: Literal["loaded", "unavailable", "invalid", "missing"]
    source_file: str | None = None
    dataset_path: str | None = None
    record_count: int = 0
    sheet_count: int = 0
    site_count: int = 0
    sites: list[str] = Field(default_factory=list)
    bands: list[str] = Field(default_factory=list)
    polarizations: list[str] = Field(default_factory=list)
    satellites: list[str] = Field(default_factory=list)
    date_range: dict[str, str | None] = Field(default_factory=lambda: {"start": None, "end": None})
    message: str


class ObservationFiltersResponse(BaseModel):
    dataset_status: Literal["loaded", "unavailable", "invalid", "missing"]
    sites: list[str] = Field(default_factory=list)
    bands: list[str] = Field(default_factory=list)
    polarizations: list[str] = Field(default_factory=list)
    satellites: list[str] = Field(default_factory=list)
    date_range: dict[str, str | None] = Field(default_factory=lambda: {"start": None, "end": None})
    message: str
