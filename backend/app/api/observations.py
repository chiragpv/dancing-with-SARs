from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.schemas.observation import (
    ObservationFiltersResponse,
    ObservationListResponse,
    ObservationSummaryResponse,
    ObservationRecordResponse,
)
from app.services.dataset_service import filter_records, load_observation_dataset, summarize_records

router = APIRouter(prefix="/api", tags=["observations"])
v1_router = APIRouter(prefix="/api/v1", tags=["observations"])


def _build_list_response(records: list, dataset_info: dict[str, object]) -> ObservationListResponse:
    return ObservationListResponse(
        dataset_status=str(dataset_info.get("dataset_status", "missing")),
        source_file=dataset_info.get("source_file"),
        dataset_path=dataset_info.get("dataset_path"),
        message=str(dataset_info.get("message", "")),
        count=len(records),
        observations=[ObservationRecordResponse.model_validate(record, from_attributes=True) for record in records],
    )


def _build_summary_response(records: list, dataset_info: dict[str, object]) -> ObservationSummaryResponse:
    summary = summarize_records(records)
    return ObservationSummaryResponse(
        dataset_status=str(dataset_info.get("dataset_status", "missing")),
        source_file=dataset_info.get("source_file"),
        dataset_path=dataset_info.get("dataset_path"),
        record_count=summary["record_count"],
        sheet_count=int(dataset_info.get("sheet_count", 0) or 0),
        site_count=summary["site_count"],
        sites=summary["sites"],
        bands=summary["bands"],
        polarizations=summary["polarizations"],
        satellites=summary["satellites"],
        date_range=summary["date_range"],
        message=str(dataset_info.get("message", "")),
    )


def _build_filters_response(records: list, dataset_info: dict[str, object]) -> ObservationFiltersResponse:
    summary = summarize_records(records)
    return ObservationFiltersResponse(
        dataset_status=str(dataset_info.get("dataset_status", "missing")),
        sites=summary["sites"],
        bands=summary["bands"],
        polarizations=summary["polarizations"],
        satellites=summary["satellites"],
        date_range=summary["date_range"],
        message=str(dataset_info.get("message", "")),
    )


@router.get("/observations", response_model=ObservationListResponse)
@v1_router.get("/observations", response_model=ObservationListResponse)
async def list_observations(
    site: Annotated[str | None, Query(description="Study site name or location.")] = None,
    year: Annotated[int | None, Query(description="Calendar year for the pass record.")] = None,
    year_from: Annotated[int | None, Query(description="Minimum year.")] = None,
    year_to: Annotated[int | None, Query(description="Maximum year.")] = None,
    date_from: Annotated[str | None, Query(description="Minimum date in ISO format.")] = None,
    date_to: Annotated[str | None, Query(description="Maximum date in ISO format.")] = None,
    satellite: Annotated[str | None, Query(description="Mission or platform name.")] = None,
    band: Annotated[str | None, Query(description="Observation band, e.g. L or S.")] = None,
    polarisation: Annotated[str | None, Query(description="Polarization, e.g. HH, VV, HV, VH.")] = None,
) -> ObservationListResponse:
    records, dataset_info = load_observation_dataset()
    filtered = filter_records(
        records,
        site=site,
        year=year,
        year_from=year_from,
        year_to=year_to,
        date_from=date_from,
        date_to=date_to,
        satellite=satellite,
        band=band,
        polarisation=polarisation,
    )
    return _build_list_response(filtered, dataset_info)


@router.get("/observations/summary", response_model=ObservationSummaryResponse)
@v1_router.get("/observations/summary", response_model=ObservationSummaryResponse)
async def observations_summary() -> ObservationSummaryResponse:
    records, dataset_info = load_observation_dataset()
    return _build_summary_response(records, dataset_info)


@router.get("/observations/filters", response_model=ObservationFiltersResponse)
@v1_router.get("/observations/filters", response_model=ObservationFiltersResponse)
async def observations_filters() -> ObservationFiltersResponse:
    records, dataset_info = load_observation_dataset()
    return _build_filters_response(records, dataset_info)


@router.get("/observations/{observation_id}", response_model=ObservationRecordResponse)
@v1_router.get("/observations/{observation_id}", response_model=ObservationRecordResponse)
async def get_observation(observation_id: str) -> ObservationRecordResponse:
    records, dataset_info = load_observation_dataset()
    for record in records:
        if record.id == observation_id:
            return ObservationRecordResponse.model_validate(record, from_attributes=True)
    raise HTTPException(status_code=404, detail=f"Observation {observation_id} not found.")
