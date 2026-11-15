from dataclasses import dataclass
from typing import Literal

from app.models.simulation import NormalizedInputs, Polarisation, RadarBand, SimulationInputs

BACKSCATTER_UNAVAILABLE_REASON = (
    "No validated measured backscatter value or supported backscatter retrieval "
    "is available from the backend."
)


@dataclass(frozen=True)
class BackscatterContext:
    inputs: SimulationInputs
    normalized_inputs: NormalizedInputs


@dataclass(frozen=True)
class BackscatterEstimate:
    value_db: float | None
    status: Literal["unavailable"]
    reason: str


def _estimate_copolarized_backscatter(
    context: BackscatterContext,
) -> BackscatterEstimate:
    del context
    return BackscatterEstimate(
        value_db=None,
        status="unavailable",
        reason=BACKSCATTER_UNAVAILABLE_REASON,
    )


def _estimate_crosspolarized_backscatter(
    context: BackscatterContext,
) -> BackscatterEstimate:
    del context
    return BackscatterEstimate(
        value_db=None,
        status="unavailable",
        reason=BACKSCATTER_UNAVAILABLE_REASON,
    )


def estimate_backscatter(
    inputs: SimulationInputs,
    normalized_inputs: NormalizedInputs,
) -> BackscatterEstimate:
    context = BackscatterContext(inputs, normalized_inputs)
    if inputs.polarisation in (Polarisation.HH, Polarisation.VV):
        return _estimate_copolarized_backscatter(context)
    return _estimate_crosspolarized_backscatter(context)
