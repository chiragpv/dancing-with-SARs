# Dancing with the SARs

A geospatial SAR exploration dashboard with a GeoStream-inspired visual direction: dark glass panels, interactive mapping, satellite-layer controls, and a focused observation workspace.

## Run locally

Requires Node.js 20+.

```bash
npm install
npm run dev
```

Open http://localhost:3000.

## Current scope

This repository currently contains the frontend foundation only. The map uses OpenStreetMap tiles and the observation controls are UI scaffolding; connect the SAR processing/data API when its endpoint and response format are ready. No backend or processing pipeline is fabricated here.

## UI inspiration

The interface takes visual inspiration from [GeoStream UI](https://github.com/Kushan-shah/geostream-ui) (glassmorphic geospatial dashboard, map-first layout, and layer controls). This project is an independent implementation; it does not copy GeoStream source code.

## Map attribution

Map tiles © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright).
