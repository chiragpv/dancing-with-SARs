"use client";

import { useEffect } from "react";
import { CircleMarker, MapContainer, TileLayer, Tooltip, useMap } from "react-leaflet";
import L from "leaflet";

type Props = { activeLayer: string; selected: string; onSelect: (id: string) => void; showEvents: boolean };

const points = [
  { id: "SAR-042", position: [22.2587, 71.1924] as [number, number], label: "Coastal morphology scan", color: "#6de6dc" },
  { id: "SAR-039", position: [26.2006, 92.9376] as [number, number], label: "Flood extent observation", color: "#f2b96f" },
  { id: "SAR-036", position: [12.9716, 77.5946] as [number, number], label: "Urban expansion analysis", color: "#a89bff" }
];

function MapResize() {
  const map = useMap();
  useEffect(() => {
    const timer = window.setTimeout(() => map.invalidateSize(), 150);
    return () => window.clearTimeout(timer);
  }, [map]);
  return null;
}

export default function ObservationMap({ activeLayer, selected, onSelect }: Props) {
  const tileUrl = activeLayer === "Optical"
    ? "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    : activeLayer === "Terrain"
      ? "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
      : "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";

  return (
    <MapContainer center={[21.5, 79.0]} zoom={5} minZoom={3} maxZoom={14} scrollWheelZoom className="leaflet-map" zoomControl={false}>
      <MapResize />
      <TileLayer key={activeLayer} url={tileUrl} attribution={activeLayer === "Terrain" ? '&copy; OpenTopoMap contributors' : activeLayer === "Optical" ? '&copy; OpenStreetMap contributors' : '&copy; CARTO'} />
      {points.map(point => (
        <CircleMarker
          key={point.id}
          center={point.position}
          radius={selected === point.id ? 10 : 7}
          pathOptions={{ color: point.color, fillColor: point.color, fillOpacity: selected === point.id ? 0.95 : 0.55, weight: selected === point.id ? 3 : 1 }}
          eventHandlers={{ click: () => onSelect(point.id) }}
        >
          <Tooltip direction="top" offset={[0, -8]}>{point.id} · {point.label}</Tooltip>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}