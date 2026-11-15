from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.observations import router as observations_router, v1_router as observations_v1_router
from app.api.simulation import router as simulation_router
from app.api.sites import router as sites_router
from app.config import Settings, get_settings
from app.logging_config import configure_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    application_settings = settings or get_settings()
    configure_logging(application_settings.log_level)

    application = FastAPI(
        title=application_settings.app_name,
        version="0.2.0",
        description="Backend API for the Dancing with the SARs project.",
    )
    if application_settings.cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=application_settings.cors_origins,
            allow_credentials=False,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
        )
    application.include_router(health_router)
    application.include_router(sites_router)
    application.include_router(simulation_router)
    application.include_router(observations_router)
    application.include_router(observations_v1_router)
    return application


app = create_app()
