import math

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.simulation import Polarisation, RadarBand, SimulationMode
from app.models.site import SiteKey
from app.schemas.simulation import SimulationRequest
from app.services.backscatter_service import BACKSCATTER_UNAVAILABLE_REASON
from app.services.simulation_service import simulate

client = TestClient(app)


@pytest.mark.parametrize(
    ("site", "expected_intensity", "max_area"),
    [
        ("brahmaputra", 0.55 * (1 - math.exp(-1)), 12_000),
        ("wayanad", 0.15 * (1 - math.exp(-1)), 800),
        ("amazon", 0.10 * (1 - math.exp(-1)), 25_000),
        ("ladakh", 0.10 * (1 - math.exp(-1)), 1_500),
    ],
)
def test_site_weights_are_applied(
    site: str, expected_intensity: float, max_area: float
) -> None:
    request = SimulationRequest(
        site=site,
        mode="pass",
        band="L",
        polarisation="VV",
        rainfall=180,
        ground_shift=0,
        thermal_stress=0,
        surface_load=0,
    )

    result = simulate(request.to_domain())

    assert result.disturbance_level == pytest.approx(expected_intensity)
    assert result.estimated_affected_area_km2 == pytest.approx(
        max_area * expected_intensity**1.3
    )


@pytest.mark.parametrize(
    ("site", "input_name", "input_value", "expected_intensity"),
    [
        ("brahmaputra", "ground_shift", 25, 0.10),
        ("brahmaputra", "thermal_stress", 6, 0.15),
        ("brahmaputra", "surface_load", 100, 0.20),
        ("wayanad", "ground_shift", 25, 0.35),
        ("wayanad", "thermal_stress", 6, 0.10),
        ("wayanad", "surface_load", 100, 0.40),
        ("amazon", "ground_shift", 25, 0.05),
        ("amazon", "thermal_stress", 6, 0.60),
        ("amazon", "surface_load", 100, 0.25),
        ("ladakh", "ground_shift", 25, 0.35),
        ("ladakh", "thermal_stress", 6, 0.40),
        ("ladakh", "surface_load", 100, 0.15),
    ],
)
def test_non_rainfall_site_weights_are_applied(
    site: str,
    input_name: str,
    input_value: float,
    expected_intensity: float,
) -> None:
    inputs = {
        "rainfall": 0,
        "ground_shift": 0,
        "thermal_stress": 0,
        "surface_load": 0,
    }
    inputs[input_name] = input_value
    request = SimulationRequest(
        site=site,
        mode="pass",
        band="L",
        polarisation="VV",
        **inputs,
    )

    assert simulate(request.to_domain()).disturbance_level == pytest.approx(
        expected_intensity
    )


def test_wayanad_applies_rainfall_and_load_interaction() -> None:
    request = SimulationRequest(
        site="wayanad",
        mode="whatif",
        band="L",
        polarisation="HH",
        rainfall=180,
        ground_shift=0,
        thermal_stress=0,
        surface_load=50,
    )

    result = simulate(request.to_domain())
    normalized_rain = 1 - math.exp(-1)

    assert result.disturbance_level == pytest.approx(
        0.15 * normalized_rain + 0.40 * 0.5 + 0.15 * normalized_rain * 0.5
    )


def test_negative_thermal_input_uses_cold_stress_normalization() -> None:
    request = SimulationRequest(
        site="amazon",
        mode="pass",
        band="L",
        polarisation="HV",
        rainfall=0,
        ground_shift=0,
        thermal_stress=-10,
        surface_load=0,
    )

    result = simulate(request.to_domain())

    assert result.disturbance_level == pytest.approx(0.45)


@pytest.mark.parametrize(
    ("band", "expected_fringe_count"),
    [("L", 12.5 / 12), ("S", 12.5 / 4.7)],
)
def test_fringe_count_uses_band_wavelength(
    band: str, expected_fringe_count: float
) -> None:
    request = SimulationRequest(
        site="brahmaputra",
        mode="pass",
        band=band,
        polarisation="VV",
        rainfall=0,
        ground_shift=12.5,
        thermal_stress=0,
        surface_load=0,
    )

    assert simulate(request.to_domain()).fringe_count == pytest.approx(
        expected_fringe_count
    )


def test_amazon_s_band_applies_coherence_decay_multiplier() -> None:
    shared = {
        "site": "amazon",
        "mode": "pass",
        "polarisation": "VV",
        "rainfall": 60,
        "ground_shift": 5,
        "thermal_stress": 2,
        "surface_load": 20,
    }
    l_band = simulate(SimulationRequest(band="L", **shared).to_domain())
    s_band = simulate(SimulationRequest(band="S", **shared).to_domain())
    rain = 1 - math.exp(-60 / 180)
    decay = 2.2 * (
        1.2 * 0.2 * 0.05
        + 0.8 * rain * 0.10
        + 0.9 * (2 / 6) * 0.60
        + 0.6 * 0.20 * 0.25
    )

    assert l_band.coherence == pytest.approx(0.95 * math.exp(-decay))
    assert s_band.coherence == pytest.approx(0.95 * math.exp(-1.3 * decay))


def test_negative_ground_shift_clamps_coherence_without_overflow() -> None:
    request = SimulationRequest(
        site="brahmaputra",
        mode="pass",
        band="L",
        polarisation="VV",
        rainfall=0,
        ground_shift=-1_000_000,
        thermal_stress=0,
        surface_load=0,
    )

    assert simulate(request.to_domain()).coherence == pytest.approx(0.95)


@pytest.mark.parametrize("site", list(SiteKey))
@pytest.mark.parametrize("band", list(RadarBand))
@pytest.mark.parametrize("polarisation", list(Polarisation))
def test_all_site_band_polarisation_combinations_are_supported(
    site: SiteKey, band: RadarBand, polarisation: Polarisation
) -> None:
    request = SimulationRequest(
        site=site,
        mode=SimulationMode.WHATIF,
        band=band,
        polarisation=polarisation,
        rainfall=35,
        ground_shift=4,
        thermal_stress=-2,
        surface_load=20,
    )

    result = simulate(request.to_domain())

    assert (result.site, result.band, result.polarisation) == (
        site,
        band,
        polarisation,
    )
    assert result.estimated_backscatter_db is None
    assert result.backscatter_status == "unavailable"
    assert result.backscatter_unavailable_reason == BACKSCATTER_UNAVAILABLE_REASON
    assert result.is_simulated is True
    assert result.data_source == "illustrative_simulation"
    assert result.acquisition_time is None


@pytest.mark.parametrize(
    ("rainfall", "thermal_stress", "expected_class"),
    [(0, 0, "Balanced"), (300, 0, "Stressed"), (0, 1000, "Critical")],
)
def test_balance_index_classification(
    rainfall: float, thermal_stress: float, expected_class: str
) -> None:
    request = SimulationRequest(
        site="brahmaputra",
        mode="pass",
        band="L",
        polarisation="VV",
        rainfall=rainfall,
        ground_shift=0,
        thermal_stress=thermal_stress,
        surface_load=0,
    )

    result = simulate(request.to_domain())

    assert result.disturbance_class == expected_class


def test_simulate_endpoint_accepts_frontend_input_aliases() -> None:
    response = client.post(
        "/api/simulate",
        json={
            "site": "wayanad",
            "mode": "whatif",
            "band": "S",
            "polarisation": "HV",
            "rain": 180,
            "shift": 12.5,
            "thermal": -4,
            "load": 35,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["site"] == "wayanad"
    assert body["balance_index"] == 53
    assert body["disturbance_class"] == "Stressed"
    assert body["estimated_backscatter_db"] is None
    assert body["backscatter_unavailable_reason"] == BACKSCATTER_UNAVAILABLE_REASON
    assert body["calculation_status"] == "partial"
