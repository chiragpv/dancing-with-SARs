# Dancing with the SARs

The integrated app is the static globe simulator in `Dancing_with_the_SARs FINALP.html` with the FastAPI service in `backend/`. The `dancing-with-SARs/` directory is a separate Next.js UI prototype and is not the integrated app.

## What the app uses

- `/api/sites` supplies the configured study sites and coordinates.
- `/api/observations` supplies 24 annual site/year input records (four sites × six years) from `SARs record-based passes 2021–2026.xlsx`. The workbook contains rainfall, shift, thermal, load, provenance, and notes—not raw SAR acquisitions. It has no acquisition dates, satellite/sensor, band/polarisation, coordinates, measured backscatter/coherence, or imagery. `/api/observations/summary` and `/api/observations/filters` supply counts and available site filters.
- `/api/simulate` supplies illustrative model outputs. These are not measured satellite observations.
- Measured backscatter is unavailable and is shown as such. Workbook years are not presented as acquisition dates when no date is provided.
- The optional local simulation feed and its recordings are generated from illustrative inputs and stored in the browser; they are not live satellite or sensor data. The app does not use a remote recording database.
- The bundled workbook is discovered automatically. Set `SAR_DATASET_PATH` in `backend/.env` to use another workbook.

## Run locally

Requires Python 3.11 or newer. From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements-dev.txt
cp -n backend/.env.example backend/.env
```

In one terminal, start the API:

```sh
cd backend
uvicorn app.main:app --reload
```

In another terminal, serve the repository root:

```sh
python3 -m http.server 8080
```

Open <http://localhost:8080/Dancing_with_the_SARs%20FINALP.html>. The page uses `http://127.0.0.1:8000` by default; set the `api` query parameter to override it, for example `?api=http://localhost:8000`. Serve the page over HTTP rather than opening it as a `file://` URL so browser CORS checks work.

API documentation is available at <http://127.0.0.1:8000/docs>. To run backend tests:

```sh
cd backend
python -m pytest
```
