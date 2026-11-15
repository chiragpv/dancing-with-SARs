from dataclasses import dataclass
from enum import Enum

from app.models.site import SiteKey


class SimulationMode(str, Enum):
    PASS = "pass"
    WHATIF = "whatif"


class RadarBand(str, Enum):
    L = "L"
    S = "S"


class Polarisation(str, Enum):
    HH = "HH"
    HV = "HV"
    VH = "VH"
    VV = "VV"


@dataclass(frozen=True)
class SimulationInputs:
    site: SiteKey
    mode: SimulationMode
    band: RadarBand
    polarisation: Polarisation
    rainfall: float
    ground_shift: float
    thermal_stress: float
    surface_load: float


@dataclass(frozen=True)
class NormalizedInputs:
    rainfall: float
    ground_shift: float
    thermal_stress: float
    surface_load: float
