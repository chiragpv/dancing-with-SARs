from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.dataset_service import load_observation_dataset

client = TestClient(app)


def test_observations_endpoint_reports_missing_workbook_without_crashing() -> None:
    response = client.get("/api/observations")

    assert response.status_code == 200
    body = response.json()
    assert body["dataset_status"] in {"missing", "unavailable", "invalid", "loaded"}
    assert body["count"] >= 0
    assert isinstance(body["observations"], list)


def test_observations_summary_and_filters_are_available() -> None:
    summary = client.get("/api/v1/observations/summary")
    filters = client.get("/api/v1/observations/filters")

    assert summary.status_code == 200
    assert filters.status_code == 200
    assert "record_count" in summary.json()
    assert "sites" in filters.json()


def test_real_workbook_records_load_and_are_exposed_by_api(monkeypatch: pytest.MonkeyPatch) -> None:
    workbook = Path(__file__).resolve().parents[2] / "SARs record-based passes 2021–2026.xlsx"
    if not workbook.exists():
        pytest.skip("Project workbook not present in workspace")

    monkeypatch.setenv("SAR_DATASET_PATH", str(workbook))
    records, info = load_observation_dataset()

    assert info["dataset_status"] == "loaded"
    assert len(records) == 24
    assert {record.site for record in records} == {"Amazon", "Brahmaputra", "Ladakh", "Wayanad"}

    response = client.get("/api/observations?site=Brahmaputra&year=2024")
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert body["observations"][0]["year"] == 2024
    assert body["observations"][0]["rainfall"] == 121.0
