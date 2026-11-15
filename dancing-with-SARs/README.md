# Standalone Next.js UI prototype

This directory contains a separate map-based UI prototype. It is not connected to the integrated app's API. The integrated globe simulator and FastAPI backend are documented in the [repository README](../README.md).

## Run locally

Requires Node.js 20+.

```bash
npm install
npm run dev
```

Open http://localhost:3000.

## Prototype scope

The map uses OpenStreetMap tiles and the observation controls are UI scaffolding. Its cards, observations, dates, locations, metrics, and sensor labels are hard-coded demo placeholders; none come from the workbook or backend. Do not interpret them as real observations or scientific measurements.

## UI inspiration

The interface takes visual inspiration from [GeoStream UI](https://github.com/Kushan-shah/geostream-ui) (glassmorphic geospatial dashboard, map-first layout, and layer controls). This project is an independent implementation; it does not copy GeoStream source code.

## Map attribution

Map tiles © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright).
