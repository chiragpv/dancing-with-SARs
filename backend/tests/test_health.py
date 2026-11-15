from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_health_reports_backend_status_and_unconfigured_dependencies() -> None:
    client = TestClient(create_app(Settings(_env_file=None, environment="test")))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "dependencies": {}}


def test_cors_uses_configured_origins() -> None:
    client = TestClient(
        create_app(
            Settings(
                _env_file=None,
                environment="test",
                cors_origins=["https://frontend.example"],
            )
        )
    )

    response = client.options(
        "/health",
        headers={
            "Origin": "https://frontend.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://frontend.example"
