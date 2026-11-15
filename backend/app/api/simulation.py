from fastapi import APIRouter

from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.services.simulation_service import simulate

router = APIRouter(prefix="/api", tags=["simulation"])


@router.post("/simulate", response_model=SimulationResponse)
async def run_simulation(request: SimulationRequest) -> SimulationResponse:
    return simulate(request.to_domain())
