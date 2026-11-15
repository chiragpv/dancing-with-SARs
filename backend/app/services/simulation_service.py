import math

from app.models.simulation import NormalizedInputs, RadarBand, SimulationInputs
from app.models.site import SiteKey
from app.schemas.simulation import SimulationResponse
from app.services.backscatter_service import estimate_backscatter

SITE_WEIGHTS: dict[SiteKey, tuple[float, float, float, float]] = {
    SiteKey.BRAHMAPUTRA: (0.55, 0.10, 0.15, 0.20),
    SiteKey.WAYANAD: (0.15, 0.35, 0.10, 0.40),
    SiteKey.AMAZON: (0.10, 0.05, 0.60, 0.25),
    SiteKey.LADAKH: (0.10, 0.35, 0.40, 0.15),
}

MAX_AFFECTED_AREA_KM2: dict[SiteKey, float] = {
    SiteKey.BRAHMAPUTRA: 12_000,
    SiteKey.WAYANAD: 800,
    SiteKey.AMAZON: 25_000,
    SiteKey.LADAKH: 1_500,
}

WAVELENGTH_CM: dict[RadarBand, float] = {
    RadarBand.L: 24.0,
    RadarBand.S: 9.4,
}


def normalize_inputs(inputs: SimulationInputs) -> NormalizedInputs:
    return NormalizedInputs(
        rainfall=1 - math.exp(-inputs.rainfall / 180),
        ground_shift=inputs.ground_shift / 25,
        thermal_stress=(
            max(0, inputs.thermal_stress) / 6
            + 0.15 * max(0, -inputs.thermal_stress) / 2
        ),
        surface_load=inputs.surface_load / 100,
    )


def simulate(inputs: SimulationInputs) -> SimulationResponse:
    normalized = normalize_inputs(inputs)
    w_rain, w_shift, w_thermal, w_load = SITE_WEIGHTS[inputs.site]

    intensity = (
        w_rain * normalized.rainfall
        + w_shift * normalized.ground_shift
        + w_thermal * normalized.thermal_stress
        + w_load * normalized.surface_load
    )
    if inputs.site is SiteKey.WAYANAD:
        intensity += 0.15 * normalized.rainfall * normalized.surface_load
    intensity = min(1.0, max(0.0, intensity))

    balance_value = 100 * (1 - intensity)
    balance_index = math.floor(balance_value + 0.5)
    if balance_index >= 70:
        disturbance_class = "Balanced"
    elif balance_index >= 40:
        disturbance_class = "Stressed"
    else:
        disturbance_class = "Critical"

    decay = 2.2 * (
        1.2 * normalized.ground_shift * w_shift
        + 0.8 * normalized.rainfall * w_rain
        + 0.9 * normalized.thermal_stress * w_thermal
        + 0.6 * normalized.surface_load * w_load
    )
    if inputs.site is SiteKey.AMAZON and inputs.band is RadarBand.S:
        decay *= 1.3
    if decay <= 0:
        coherence = 0.95
    elif decay >= math.log(19):
        coherence = 0.05
    else:
        coherence = 0.95 * math.exp(-decay)

    fringe_count = inputs.ground_shift / (WAVELENGTH_CM[inputs.band] / 2)
    affected_area = MAX_AFFECTED_AREA_KM2[inputs.site] * intensity**1.3
    backscatter = estimate_backscatter(inputs, normalized)

    return SimulationResponse(
        site=inputs.site,
        mode=inputs.mode,
        band=inputs.band,
        polarisation=inputs.polarisation,
        balance_index=balance_index,
        disturbance_level=intensity,
        disturbance_class=disturbance_class,
        estimated_affected_area_km2=affected_area,
        coherence=coherence,
        fringe_count=fringe_count,
        estimated_backscatter_db=backscatter.value_db,
        backscatter_status=backscatter.status,
        backscatter_unavailable_reason=backscatter.reason,
        calculation_status="partial",
        data_source="illustrative_simulation",
        is_simulated=True,
        acquisition_time=None,
        processing_status="illustrative_only",
    )
