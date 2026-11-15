from datetime import date, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook

from app.config import Settings
from app.main import app
from app.models.observation import ObservationRecord
from app.services import dataset_service
from app.services.dataset_service import (
    _convert_sheet_to_records,
    filter_records,
    load_observation_dataset,
)

client = TestClient(app)


def test_observations_endpoint_reports_missing_workbook_without_crashing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.services.dataset_service._resolve_dataset_path",
        lambda: None,
    )

    response = client.get("/api/observations")

    assert response.status_code == 200
    body = response.json()
    assert body["dataset_status"] == "missing"
    assert body["count"] == 0
    assert body["observations"] == []


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
    assert all(record.acquisition_time is None for record in records)
    summary = client.get("/api/observations/summary").json()
    assert summary["date_range"] == {"start": None, "end": None}
    date_filtered = client.get(
        "/api/observations?date_from=2024-01-01&date_to=2024-12-31"
    )
    assert date_filtered.status_code == 200
    assert date_filtered.json()["count"] == 0


def test_year_only_rows_do_not_create_dates_and_keep_zero_values() -> None:
    records = _convert_sheet_to_records(
        "Passes",
        [("Site", "Year", "Rainfall (mm)"), ("Brahmaputra", 2024, 0)],
        "records.xlsx",
    )

    assert len(records) == 1
    assert records[0].acquisition_time is None
    assert records[0].rainfall == 0


def test_explicit_acquisition_date_is_preserved() -> None:
    records = _convert_sheet_to_records(
        "Passes",
        [
            ("Site", "Year", "Pass date"),
            ("Brahmaputra", 2024, datetime(2024, 7, 5, 12, 30)),
        ],
        "records.xlsx",
    )

    assert records[0].acquisition_time == "2024-07-05T12:30:00"


def test_date_and_year_ranges_exclude_records_without_matching_metadata() -> None:
    records = [
        ObservationRecord(
            id="dated",
            site="Brahmaputra",
            year=2024,
            acquisition_time="2024-07-05T12:30:00",
        ),
        ObservationRecord(id="undated", site="Brahmaputra", year=2024),
        ObservationRecord(id="unknown-year", site="Brahmaputra"),
    ]

    filtered = filter_records(
        records,
        year_from=2024,
        date_from=date(2024, 7, 5),
        date_to=date(2024, 7, 5),
    )

    assert [record.id for record in filtered] == ["dated"]


def test_configured_workbook_path_is_loaded_from_settings(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    workbook_path = tmp_path / "custom-passes.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Site", "Year", "Rainfall (mm)"])
    sheet.append(["Brahmaputra", 2024, 0])
    workbook.save(workbook_path)
    env_file = tmp_path / ".env"
    env_file.write_text(f'SAR_DATASET_PATH="{workbook_path}"\n', encoding="utf-8")
    monkeypatch.delenv("SAR_DATASET_PATH", raising=False)
    monkeypatch.delenv("SAR_DATASET_FILE", raising=False)
    settings = Settings(_env_file=env_file)
    monkeypatch.setattr(
        dataset_service,
        "get_settings",
        lambda: settings,
    )

    records, info = load_observation_dataset()

    assert info["dataset_status"] == "loaded"
    assert info["source_file"] == workbook_path.name
    assert len(records) == 1
    assert records[0].acquisition_time is None
    assert records[0].rainfall == 0
