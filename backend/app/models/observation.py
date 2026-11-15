from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ObservationRecord:
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
    metadata: dict[str, Any] = field(default_factory=dict)
