from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_sites_endpoint_returns_configured_sites_and_coordinates() -> None:
    response = client.get("/api/sites")

    assert response.status_code == 200
    sites = {site["key"]: site for site in response.json()}
    assert set(sites) == {"brahmaputra", "wayanad", "amazon", "ladakh"}
    assert (sites["brahmaputra"]["latitude"], sites["brahmaputra"]["longitude"]) == (
        26.2,
        91.7,
    )
    assert (sites["wayanad"]["latitude"], sites["wayanad"]["longitude"]) == (
        11.6,
        76.1,
    )
    assert (sites["amazon"]["latitude"], sites["amazon"]["longitude"]) == (-9, -63)
    assert (sites["ladakh"]["latitude"], sites["ladakh"]["longitude"]) == (34.2, 77.6)
    assert all(site["description"] for site in sites.values())
