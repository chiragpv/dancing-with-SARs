from __future__ import annotations

import os
import re
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

from app.models.observation import ObservationRecord

DATASET_FILENAME = "SARs record-based passes 2021–2026.xlsx"
ALTERNATE_DATASET_FILENAMES = (
    "SARs record-based passes 2021-2026.xlsx",
    "SARs record-based passes.xlsx",
    "sar-record-based-passes.xlsx",
)


def _normalize_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")


def _normalize_scalar(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "item") and not isinstance(value, (str, bytes)):
        try:
            value = value.item()
        except (TypeError, ValueError):
            pass
    if isinstance(value, float) and value != value:
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    return value


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    text = text.replace(",", "").replace("%", "")
    try:
        return float(text)
    except ValueError:
        return None


def _as_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def _parse_date(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return None
        try:
            return datetime.fromisoformat(cleaned.replace("Z", "+00:00")).isoformat()
        except ValueError:
            pass
        try:
            return datetime.strptime(cleaned, "%Y-%m-%d %H:%M:%S").isoformat()
        except ValueError:
            pass
        try:
            return datetime.strptime(cleaned, "%Y-%m-%d").isoformat()
        except ValueError:
            pass
    return None


def _normalize_site(raw_value: Any) -> str | None:
    if raw_value is None:
        return None
    text = str(raw_value).strip()
    if not text:
        return None
    return text


def _resolve_dataset_path() -> Path | None:
    configured = os.getenv("SAR_DATASET_PATH") or os.getenv("SAR_DATASET_FILE")
    if configured:
        candidate = Path(configured).expanduser().resolve()
        if candidate.exists():
            return candidate

    search_roots = [
        Path.cwd(),
        Path(__file__).resolve().parents[2],
        Path(__file__).resolve().parents[3],
    ]

    seen: set[Path] = set()
    for root in search_roots:
        for name in [DATASET_FILENAME, *ALTERNATE_DATASET_FILENAMES]:
            candidate = root / name
            if candidate.exists() and candidate not in seen:
                return candidate
            seen.add(candidate)
        for match in root.rglob("*.xlsx"):
            lower = match.name.lower()
            if "sar" in lower and "pass" in lower:
                return match
    return None


def _derive_record_id(sheet_name: str, row_index: int, raw: dict[str, Any]) -> str:
    for key in ("observation_id", "id", "record_id", "pass_id"):
        value = raw.get(key)
        if value not in (None, ""):
            return str(value)
    for key in ("site", "study_site", "location", "year"):
        value = raw.get(key)
        if value not in (None, ""):
            return f"{sheet_name}-{value}-{row_index}"
    return f"{sheet_name}-{row_index}"


def _convert_sheet_to_records(sheet_name: str, rows: list[tuple[Any, ...]], source_file: str) -> list[ObservationRecord]:
    records: list[ObservationRecord] = []
    if not rows:
        return records

    header = [str(value).strip() if value is not None else "" for value in rows[0]]
    normalized_header = {_normalize_key(value): value for value in header if value}
    if "site" not in normalized_header and "study_site" not in normalized_header and "location" not in normalized_header:
        return records
    if "year" not in normalized_header and "calendar_year" not in normalized_header and "pass_date" not in normalized_header and "date" not in normalized_header:
        return records
    for row_index, row in enumerate(rows[1:], start=2):
        if not any(value is not None for value in row):
            continue
        raw = {header[idx]: value for idx, value in enumerate(row) if idx < len(header)}
        cleaned = { _normalize_key(key): _normalize_scalar(value) for key, value in raw.items() }
        site = _normalize_site(
            cleaned.get("site")
            or cleaned.get("study_site")
            or cleaned.get("location")
            or cleaned.get("site_name")
        )
        year = _as_int(cleaned.get("year") or cleaned.get("calendar_year"))
        if site is None and year is not None:
            continue

        record = ObservationRecord(
            id=_derive_record_id(sheet_name, row_index, cleaned),
            site=site,
            year=year,
            source_file=source_file,
            source_sheet=sheet_name,
            source_row=row_index,
            acquisition_time=datetime(year, 1, 1).isoformat() if year is not None else None,
            satellite=cleaned.get("satellite") or cleaned.get("mission") or cleaned.get("sensor") or cleaned.get("platform"),
            band=cleaned.get("band") or cleaned.get("frequency_band") or cleaned.get("sensor_band"),
            polarisation=cleaned.get("polarisation") or cleaned.get("polarization") or cleaned.get("pol"),
            latitude=_normalize_scalar(cleaned.get("latitude") or cleaned.get("lat")),
            longitude=_normalize_scalar(cleaned.get("longitude") or cleaned.get("lon") or cleaned.get("lng")),
            backscatter_db=_normalize_scalar(cleaned.get("backscatter_db") or cleaned.get("sigma_0") or cleaned.get("backscatter")),
            coherence=_normalize_scalar(cleaned.get("coherence") or cleaned.get("interferometric_coherence")),
            rainfall=_as_float(cleaned.get("rainfall") or cleaned.get("rainfall_mm") or cleaned.get("rain_mm") or cleaned.get("precipitation_mm")),
            soil_moisture=_as_float(cleaned.get("soil_moisture") or cleaned.get("soil_moisture_pct")),
            metadata={
                key: value
                for key, value in cleaned.items()
                if key not in {
                    "site",
                    "study_site",
                    "location",
                    "site_name",
                    "year",
                    "calendar_year",
                    "acquisition_time",
                    "acquisition_date",
                    "pass_date",
                    "date",
                    "timestamp",
                    "satellite",
                    "mission",
                    "sensor",
                    "platform",
                    "band",
                    "frequency_band",
                    "sensor_band",
                    "polarisation",
                    "polarization",
                    "pol",
                    "latitude",
                    "lat",
                    "longitude",
                    "lon",
                    "lng",
                    "backscatter_db",
                    "sigma_0",
                    "backscatter",
                    "coherence",
                    "interferometric_coherence",
                    "rainfall",
                    "rain_mm",
                    "precipitation_mm",
                    "soil_moisture",
                    "soil_moisture_pct",
                }
            },
        )
        if site is not None:
            record.metadata["from_records"] = raw.get("From records")
            record.metadata["note"] = raw.get("Note")
            record.metadata["shift_cm"] = _as_float(raw.get("Shift (cm)"))
            record.metadata["thermal_c"] = _as_float(raw.get("Thermal (°C)"))
            record.metadata["load_percent"] = _as_float(raw.get("Load (%)"))
            records.append(record)
    return records


def load_observation_dataset() -> tuple[list[ObservationRecord], dict[str, Any]]:
    dataset_path = _resolve_dataset_path()
    if dataset_path is None:
        return [], {
            "dataset_status": "missing",
            "source_file": None,
            "dataset_path": None,
            "message": "No SAR Excel workbook was found. Set SAR_DATASET_PATH to the workbook path or place the workbook in the project root.",
            "sheet_count": 0,
            "sheets": [],
            "records": [],
            "invalid_rows": 0,
        }

    try:
        workbook = load_workbook(dataset_path, read_only=True, data_only=True)
        sheet_names = workbook.sheetnames
        records: list[ObservationRecord] = []
        invalid_rows = 0
        for sheet_name in sheet_names:
            sheet = workbook[sheet_name]
            rows = list(sheet.iter_rows(values_only=True))
            if not rows:
                continue
            try:
                records.extend(_convert_sheet_to_records(sheet_name, rows, dataset_path.name))
            except Exception:
                invalid_rows += 1
        return records, {
            "dataset_status": "loaded",
            "source_file": dataset_path.name,
            "dataset_path": str(dataset_path),
            "message": f"Loaded {len(records)} record(s) from {dataset_path.name}.",
            "sheet_count": len(sheet_names),
            "sheets": sheet_names,
            "records": records,
            "invalid_rows": invalid_rows,
        }
    except Exception as exc:  # pragma: no cover - environment specific
        return [], {
            "dataset_status": "invalid",
            "source_file": dataset_path.name,
            "dataset_path": str(dataset_path),
            "message": f"The workbook could not be opened: {exc}",
            "sheet_count": 0,
            "sheets": [],
            "records": [],
            "invalid_rows": 0,
        }


def filter_records(
    records: Iterable[ObservationRecord],
    *,
    site: str | None = None,
    year: int | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    satellite: str | None = None,
    band: str | None = None,
    polarisation: str | None = None,
) -> list[ObservationRecord]:
    filtered: list[ObservationRecord] = []
    for record in records:
        if site and (record.site or "").lower() != site.lower():
            continue
        if year is not None and record.year != year:
            continue
        if year_from is not None and record.year is not None and record.year < year_from:
            continue
        if year_to is not None and record.year is not None and record.year > year_to:
            continue
        if satellite and (record.satellite or "").lower() != satellite.lower():
            continue
        if band and (record.band or "").upper() != band.upper():
            continue
        if polarisation and (record.polarisation or "").upper() != polarisation.upper():
            continue

        candidate_date = record.acquisition_time
        if isinstance(candidate_date, datetime):
            date_value = candidate_date.isoformat()
        else:
            date_value = str(candidate_date) if candidate_date else None

        if date_from and date_value and date_value < date_from:
            continue
        if date_to and date_value and date_value > date_to:
            continue
        filtered.append(record)
    return filtered


def summarize_records(records: Iterable[ObservationRecord]) -> dict[str, Any]:
    record_list = list(records)

    sites = sorted({record.site for record in record_list if record.site})
    bands = sorted({str(record.band).upper() for record in record_list if record.band})
    polarizations = sorted({str(record.polarisation).upper() for record in record_list if record.polarisation})
    satellites = sorted({str(record.satellite) for record in record_list if record.satellite})

    date_values = [
        record.acquisition_time for record in record_list if record.acquisition_time is not None
    ]
    start = min(str(value) for value in date_values) if date_values else None
    end = max(str(value) for value in date_values) if date_values else None

    return {
        "record_count": len(record_list),
        "site_count": len(sites),
        "sites": sites,
        "bands": bands,
        "polarizations": polarizations,
        "satellites": satellites,
        "date_range": {"start": start, "end": end},
    }
