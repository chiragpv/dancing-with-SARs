# Dancing with the SARs backend

This directory contains a modular FastAPI backend. It provides app configuration, environment-driven CORS, structured JSON logging, health reporting, four configured sites, workbook-backed historical records, and an explicitly **illustrative** simulation endpoint.

The static simulator at the repository root (`Dancing_with_the_SARs FINALP.html`) calls this API for site metadata, workbook records, and simulation results. The equations are illustrative outputs, not measurements or retrieved satellite data. Backscatter remains `null` with an explicit unavailable reason; no backscatter value is inferred.

The separate Next.js demonstration dashboard in `dancing-with-SARs/` still contains its own sample UI and is not connected to these endpoints.

## Requirements

- Python 3.11 or newer

## Setup and run

From this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

The example `.env` allows the local static frontend origins `http://localhost:8080` and `http://127.0.0.1:8080`. Use the exact origin from your browser in `CORS_ORIGINS` when hosting the page elsewhere.

Interactive API documentation is available at `/docs`.

## Run the connected simulator

Start the backend from this directory using the setup above. In a separate terminal, serve the repository root (do not open the HTML as a `file://` URL, which does not provide a usable CORS origin):

```powershell
Set-Location ..
python -m http.server 8080
```

Open `http://localhost:8080/Dancing_with_the_SARs%20FINALP.html`. The page uses `http://127.0.0.1:8000` by default; override it with `window.SARS_API_BASE` before the module script or the `?api=http://host:port` query parameter.

## API

### `GET /health`

Example response:

```json
{
  "status": "ok",
  "dependencies": {}
}
```

No external dependencies are configured yet, so the dependency health map is empty.

### `GET /api/observations`

Returns any workbook-backed historical SAR records when the Excel dataset is available. If no workbook is present, the endpoint returns a structured empty result with `dataset_status` set to `missing` or `unavailable` instead of fabricating observations.

The simulator uses these workbook endpoints:

- `GET /api/observations` to populate historical record browsing and year-specific pass inputs.
- `GET /api/observations/summary` to report the loaded record count.
- `GET /api/observations/filters` to populate the site filters.
- The same observation list, summary, and filter routes are also available under `/api/v1`.

Workbook-provided rainfall, shift, thermal, load, provenance, and notes are displayed as recorded. The workbook does not contain measured SAR backscatter or affected-area values; the UI does not represent modelled area as recorded area.

### `GET /api/sites`

Returns project-configured site keys, names, coordinates, and descriptions. These are point coordinates from the project brief, not satellite footprints or acquired observations.

Example response:

```json
[
  {
    "key": "brahmaputra",
    "name": "Brahmaputra",
    "latitude": 26.2,
    "longitude": 91.7,
    "description": "Project-configured illustrative observation point. Coordinates do not define a satellite acquisition footprint."
  }
]
```

### `POST /api/simulate`

Example request:

```json
{
  "site": "brahmaputra",
  "mode": "whatif",
  "band": "L",
  "polarisation": "VV",
  "rainfall": 0,
  "ground_shift": 0,
  "thermal_stress": 0,
  "surface_load": 0
}
```

The short input names `rain`, `shift`, `thermal`, and `load` are also accepted for the original simulator's input contract. `polarization` is accepted as an alternate spelling for `polarisation`. Both `pass` and `whatif` modes apply the same supplied equations because no different `pass` formula or real pass data was supplied; the mode is echoed in the response.

Example response:

```json
{
  "site": "brahmaputra",
  "mode": "whatif",
  "band": "L",
  "polarisation": "VV",
  "balance_index": 100,
  "disturbance_level": 0.0,
  "disturbance_class": "Balanced",
  "estimated_affected_area_km2": 0.0,
  "coherence": 0.95,
  "fringe_count": 0.0,
  "estimated_backscatter_db": null,
  "backscatter_status": "unavailable",
  "backscatter_unavailable_reason": "No validated measured backscatter value or supported backscatter retrieval is available from the backend.",
  "calculation_status": "partial",
  "data_source": "illustrative_simulation",
  "is_simulated": true,
  "acquisition_time": null,
  "processing_status": "illustrative_only"
}
```

The co-polarized (`HH`, `VV`) and cross-polarized (`HV`, `VH`) backscatter paths are separated in the service so the original equations can be added when available. They currently return no value.

### Frontend field mapping

| Existing simulator field | API field |
| --- | --- |
| `rain`, `shift`, `thermal`, `load` | `rainfall`, `ground_shift`, `thermal_stress`, `surface_load` (both forms accepted) |
| `I` | `disturbance_level` |
| `B` | `balance_index` |
| `fringes` | `fringe_count` |
| `coh` | `coherence` |
| `area` | `estimated_affected_area_km2` |
| `sig` | `estimated_backscatter_db` (currently `null`; original equation unavailable) |

The static simulator's current dashboard values use this response. Backscatter is displayed as unavailable. The Next.js demo does not use this simulator contract.

The static frontend also calls `GET /health` and `GET /api/sites` during startup. The site's displayed coordinates and names come from the API.

## Tests

```powershell
python -m pytest
```

Tests cover site metadata, the simulation formulas, all site/band/polarisation combinations, input aliases, classification, and explicit backscatter unavailability.

## Scope and next phases

Phase 2 does not include repeat-pass analysis, a database, storage, providers, weather, or raster processing. No observation IDs, acquisition timestamps, orbital metadata, or measured values are fabricated.
