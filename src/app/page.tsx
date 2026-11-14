"use client";

import dynamic from "next/dynamic";
import { useMemo, useState } from "react";
import {
  Activity, ArrowDownRight, ArrowUpRight, Bell, CalendarDays, ChevronDown,
  Crosshair, Download, Layers3, MapPin, Menu, Radar, Search, Settings2,
  SlidersHorizontal, Satellite, Sparkles, Waves, X
} from "lucide-react";

const ObservationMap = dynamic(() => import("@/components/ObservationMap"), {
  ssr: false,
  loading: () => <div className="map-loading">Preparing geospatial workspace…</div>
});

const observations = [
  { id: "SAR-042", name: "Coastal morphology scan", place: "Gujarat coastline, India", date: "14 Nov 2026", status: "Ready", change: "+12.8%", type: "Coastline" },
  { id: "SAR-039", name: "Flood extent observation", place: "Assam, India", date: "12 Nov 2026", status: "Processing", change: "+8.4%", type: "Flooding" },
  { id: "SAR-036", name: "Urban expansion analysis", place: "Bengaluru, India", date: "10 Nov 2026", status: "Ready", change: "+3.2%", type: "Urban" }
];

export default function Home() {
  const [activeLayer, setActiveLayer] = useState("SAR intensity");
  const [selected, setSelected] = useState("SAR-042");
  const [range, setRange] = useState("30 days");
  const [search, setSearch] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const filtered = useMemo(() => observations.filter(o => (o.name + o.place + o.type).toLowerCase().includes(search.toLowerCase())), [search]);
  const current = observations.find(o => o.id === selected) ?? observations[0];

  return (
    <main className="shell">
      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-mark"><Radar size={21} strokeWidth={1.8} /></div>
          <div><strong>DANCING WITH THE SARs</strong><span>EARTH OBSERVATION LAB</span></div>
          <button className="icon-btn mobile-close" onClick={() => setSidebarOpen(false)} aria-label="Close menu"><X size={18}/></button>
        </div>
        <div className="workspace-label">WORKSPACE</div>
        <button className="nav-item active"><Crosshair size={17}/> Observation console <span className="nav-dot"/></button>
        <button className="nav-item"><Layers3 size={17}/> Data layers</button>
        <button className="nav-item"><Activity size={17}/> Change analysis</button>
        <button className="nav-item"><CalendarDays size={17}/> Timeline</button>
        <div className="sidebar-divider"/>
        <div className="workspace-label">YOUR COLLECTION</div>
        <button className="collection-item"><span className="collection-icon cyan"><Waves size={15}/></span><span>Coastal monitoring</span><span className="collection-count">08</span></button>
        <button className="collection-item"><span className="collection-icon violet"><Satellite size={15}/></span><span>Urban change</span><span className="collection-count">12</span></button>
        <button className="collection-item"><span className="collection-icon amber"><Activity size={15}/></span><span>Flood watch</span><span className="collection-count">04</span></button>
        <div className="sidebar-bottom">
          <div className="status-card"><span className="pulse"/><div><b>Workspace online</b><small>Map services available</small></div></div>
          <button className="nav-item"><Settings2 size={17}/> Settings</button>
          <div className="profile"><div className="avatar">DW</div><div><b>Research workspace</b><small>Local session</small></div><ChevronDown size={15}/></div>
        </div>
      </aside>

      <section className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <button className="icon-btn mobile-menu" onClick={() => setSidebarOpen(true)} aria-label="Open menu"><Menu size={19}/></button>
            <div className="breadcrumb">Workspace <span>/</span> <b>Observation console</b></div>
          </div>
          <div className="topbar-actions">
            <div className="live-pill"><span className="pulse"/> DEMO MODE</div>
            <button className="icon-btn" aria-label="Notifications"><Bell size={17}/><i/></button>
            <div className="avatar small">DW</div>
          </div>
        </header>

        <div className="content">
          <div className="page-heading">
            <div><div className="eyebrow"><span/> SATELLITE INTELLIGENCE / UI PREVIEW</div><h1>Observation <em>console</em></h1><p>Explore the surface. Detect the signal. Understand the change.</p></div>
            <div className="heading-actions"><button className="secondary-btn"><CalendarDays size={15}/> Nov 01 — Nov 14, 2026 <ChevronDown size={14}/></button><button className="primary-btn"><Sparkles size={15}/> New analysis</button></div>
          </div>

          <div className="stats-grid">
            <div className="stat-card"><div className="stat-top"><span>DEMO OBSERVATIONS</span><span className="stat-icon"><Satellite size={16}/></span></div><div className="stat-value">1,284 <small className="positive"><ArrowUpRight size={13}/> 12.6%</small></div><div className="stat-foot">Across all monitored regions</div><div className="sparkline"><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/></div></div>
            <div className="stat-card"><div className="stat-top"><span>SAMPLE CHANGE AREAS</span><span className="stat-icon"><Activity size={16}/></span></div><div className="stat-value">36 <small className="positive"><ArrowUpRight size={13}/> 4.8%</small></div><div className="stat-foot">Detected in selected period</div><div className="mini-bars"><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/></div></div>
            <div className="stat-card"><div className="stat-top"><span>SAMPLE COVERAGE</span><span className="stat-icon"><Layers3 size={16}/></span></div><div className="stat-value">92.4<small>%</small></div><div className="stat-foot">Selected region coverage</div><div className="coverage-line"><span/></div></div>
            <div className="stat-card"><div className="stat-top"><span>SENSOR UI PREVIEW</span><span className="stat-icon"><Radar size={16}/></span></div><div className="stat-value">04 <small className="muted-stat">/ 06</small></div><div className="stat-foot">SAR data sources connected</div><div className="sensor-dots"><i/><i/><i/><i/><i/><i/></div></div>
          </div>

          <div className="dashboard-grid">
            <section className="panel map-panel">
              <div className="panel-header"><div><div className="panel-kicker">GEOSPATIAL VIEW</div><h2>Surface intelligence</h2></div><div className="panel-tools"><button className="tool-btn"><SlidersHorizontal size={14}/> Controls</button><button className="icon-btn"><Download size={16}/></button><button className="icon-btn"><span>···</span></button></div></div>
              <div className="map-toolbar"><div className="layer-tabs">{["SAR intensity","Optical","Terrain"].map(layer => <button key={layer} onClick={() => setActiveLayer(layer)} className={activeLayer === layer ? "selected" : ""}>{layer}</button>)}</div><div className="map-meta"><span className="live-dot"/> {activeLayer.toUpperCase()} <span className="meta-sep">•</span> EPSG:4326</div></div>
              <div className="map-wrap"><ObservationMap activeLayer={activeLayer} selected={selected} onSelect={setSelected} /><div className="map-coordinates"><Crosshair size={12}/> 22.2587° N, 71.1924° E</div><div className="map-legend"><span className="legend-title">INTENSITY</span><div className="legend-gradient"/><div className="legend-values"><span>LOW</span><span>HIGH</span></div></div><div className="map-float"><span className="pulse"/> MAP READY</div></div>
              <div className="map-footer"><span><MapPin size={13}/> {current.place}</span><span>Zoom level 6.5</span><span>Tiles © OpenStreetMap</span></div>
            </section>

            <section className="panel detail-panel">
              <div className="panel-header"><div><div className="panel-kicker">SELECTED OBSERVATION</div><h2>Signal overview</h2></div><button className="icon-btn"><span>···</span></button></div>
              <div className="observation-id"><span className="id-mark"><Radar size={17}/></span><div><b>{current.id}</b><small>{current.type} monitoring</small></div><span className={`status-tag ${current.status === "Ready" ? "ready" : "processing"}`}>{current.status}</span></div>
              <div className="detail-location"><MapPin size={14}/><span>{current.place}</span></div>
              <div className="detail-image"><div className="radar-art"><div className="radar-ring r1"/><div className="radar-ring r2"/><div className="radar-ring r3"/><div className="radar-sweep"/><div className="radar-center"/></div><div className="image-label">SAR BACKSCATTER / PREVIEW</div></div>
              <div className="detail-metrics"><div><small>CHANGE SIGNAL</small><b className="metric-positive">{current.change}</b></div><div><small>ACQUISITION</small><b>14 NOV 2026</b></div><div><small>CONFIDENCE</small><b>High · 94%</b></div></div>
              <button className="full-btn">Open observation details <ArrowDownRight size={15}/></button>
            </section>
          </div>

          <div className="bottom-grid">
            <section className="panel observations-panel">
              <div className="panel-header"><div><div className="panel-kicker">RECENT ACTIVITY</div><h2>Latest observations <span className="count-badge">03</span></h2></div><button className="text-btn">View all <ArrowUpRight size={14}/></button></div>
              <div className="table-controls"><div className="search-box"><Search size={14}/><input placeholder="Search observations…" value={search} onChange={e => setSearch(e.target.value)}/></div><button className="tool-btn" onClick={() => setRange(range === "30 days" ? "7 days" : "30 days")}>{range} <ChevronDown size={13}/></button></div>
              <div className="observation-list">{filtered.map(o => <button key={o.id} className={`observation-row ${selected === o.id ? "row-active" : ""}`} onClick={() => setSelected(o.id)}><span className="row-symbol"><Radar size={16}/></span><span className="row-main"><b>{o.name}</b><small>{o.place} · {o.date}</small></span><span className="row-change">{o.change}</span><span className={`status-tag ${o.status === "Ready" ? "ready" : "processing"}`}>{o.status}</span><ChevronDown className="row-chevron" size={15}/></button>)}{filtered.length === 0 && <div className="empty-state">No observations match that search.</div>}</div>
            </section>
            <section className="panel layers-panel">
              <div className="panel-header"><div><div className="panel-kicker">DATA CONFIGURATION</div><h2>Map layers</h2></div><button className="icon-btn"><Layers3 size={16}/></button></div>
              <div className="layer-list">
                <button className={activeLayer === "SAR intensity" ? "layer-row layer-active" : "layer-row"} onClick={() => setActiveLayer("SAR intensity")}><span className="layer-swatch sar-swatch"/><span><b>SAR intensity</b><small>Sentinel-1 · VV / VH</small></span><span className="toggle on"/></button>
                <button className={activeLayer === "Optical" ? "layer-row layer-active" : "layer-row"} onClick={() => setActiveLayer("Optical")}><span className="layer-swatch optical-swatch"/><span><b>Optical imagery</b><small>True colour composite</small></span><span className={activeLayer === "Optical" ? "toggle on" : "toggle"}/></button>
                <button className={activeLayer === "Terrain" ? "layer-row layer-active" : "layer-row"} onClick={() => setActiveLayer("Terrain")}><span className="layer-swatch terrain-swatch"/><span><b>Terrain model</b><small>Elevation &amp; contours</small></span><span className={activeLayer === "Terrain" ? "toggle on" : "toggle"}/></button>
              </div>
              <div className="layer-note"><Sparkles size={14}/><span>Sample dashboard values only. Connect your SAR API to display real observations and backscatter layers.</span></div>
            </section>
          </div>
          <footer className="footer"><span>© 2026 DANCING WITH THE SARs</span><span>GEOSPATIAL INTELLIGENCE WORKSPACE <i/> BUILD 0.1.0</span></footer>
        </div>
      </section>
    </main>
  );
}