from datetime import datetime
from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from app.models.simulation import (
    Polarisation,
    RadarBand,
    SimulationInputs,
    SimulationMode,
)
from app.models.site import SiteKey


class SimulationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    site: SiteKey
    mode: SimulationMode
    band: RadarBand
    polarisation: Polarisation = Field(
        validation_alias=AliasChoices("polarisation", "polarization")
    )
    rainfall: float = Field(
        validation_alias=AliasChoices("rainfall", "rain"),
        ge=0,
        description="Rainfall model input; normalized using rain / 180.",
    )
    ground_shift: float = Field(
        validation_alias=AliasChoices("ground_shift", "shift"),
        description="Ground-shift input in centimetres, matching the supplied wavelengths.",
    )
    thermal_stress: float = Field(
        validation_alias=AliasChoices("thermal_stress", "thermal"),
        description="Thermal-stress model input, normalized by the supplied formula.",
    )
    surface_load: float = Field(
        validation_alias=AliasChoices("surface_load", "load"),
        ge=0,
        description="Surface-load model input; normalized using load / 100.",
    )

    def to_domain(self) -> SimulationInputs:
        return SimulationInputs(
            site=self.site,
            mode=self.mode,
            band=self.band,
            polarisation=self.polarisation,
            rainfall=self.rainfall,
            ground_shift=self.ground_shift,
            thermal_stress=self.thermal_stress,
            surface_load=self.surface_load,
        )


class SimulationResponse(BaseModel):
    site: SiteKey
    mode: SimulationMode
    band: RadarBand
    polarisation: Polarisation
    balance_index: int = Field(ge=0, le=100)
    disturbance_level: float = Field(ge=0, le=1)
    disturbance_class: Literal["Balanced", "Stressed", "Critical"]
    estimated_affected_area_km2: float = Field(ge=0)
    coherence: float = Field(ge=0.05, le=0.95)
    fringe_count: float
    estimated_backscatter_db: float | None
    backscatter_status: Literal["unavailable"]
    backscatter_unavailable_reason: str
    calculation_status: Literal["partial"]
    data_source: Literal["illustrative_simulation"]
    is_simulated: Literal[True]
    acquisition_time: datetime | None
    processing_status: Literal["illustrative_only"]
