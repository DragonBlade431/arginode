import React, { useEffect, useState } from "react";
import "./LiveFeed.css";
import MapDisplay from "./MapDisplay";

export default function LiveFeed({ data, setData, pred, setPred }) {
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws/live");

    ws.onmessage = (e) => {
      try {
        const d = JSON.parse(e.data);
        setData(d.inputs || {});
        setPred(d);
      } catch {}
    };

    return () => ws.close();
  }, [setData, setPred]);

  const togglePause = async () => {
    const r = await fetch("http://127.0.0.1:8000/toggle_pause", { method: "POST" });
    const d = await r.json();
    setIsPaused(d.paused);
  };

  const isLive = pred.field_type === "Arduino Field";

  return (
    <div className="dashboard-grid" style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '30px', width: '100%' }}>
      <div className="stacked" style={{ gap: '30px' }}>
        <div className="glass-card live-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
            <h2 style={{ margin: 0 }}>Field Intelligence</h2>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button 
                onClick={togglePause}
                style={{
                  background: isPaused ? '#ef4444' : '#f1f5f9',
                  color: isPaused ? '#fff' : '#475569',
                  border: '1px solid var(--border)',
                  padding: '8px 16px',
                  borderRadius: '8px',
                  fontSize: '12px',
                  fontWeight: '700',
                  cursor: 'pointer'
                }}
              >
                {isPaused ? '▶ RESUME FEED' : '⏸ PAUSE FEED'}
              </button>
              <div className={`source-badge ${isLive ? "live" : "demo"}`} style={{ position: 'static' }}>
                {isLive ? "Hardware Connected" : "Demo Mode"}
              </div>
            </div>
          </div>

          <div className="sensor-grid">
            {[
              { k: "N", u: "mg/kg", l: "Nitrogen" },
              { k: "P", u: "mg/kg", l: "Phosphorus" },
              { k: "K", u: "mg/kg", l: "Potassium" },
              { k: "pH", l: "Soil pH" },
              { k: "temperature", l: "Temp", u: "°C" },
              { k: "humidity", l: "Humidity", u: "%" },
              { k: "rainfall", l: "Rainfall", u: "mm" },
            ].map(({ k, l, u }) => (
              <div key={k} className="sensor-box stacked">
                <span className="sensor-label">{l}</span>
                <div className="sensor-value-group">
                  <span className="sensor-value">{data?.[k] ?? "0.0"}</span>
                  {u && <span className="sensor-unit">{u}</span>}
                </div>
              </div>
            ))}
          </div>

          <div className="ai-box" style={{ display: 'flex', gap: '30px', alignItems: 'center', minHeight: '180px' }}>
            <div style={{ flex: 1 }}>
              <div className="ai-label">AI Inference Results</div>
              <div className="crop" style={{ fontSize: '32px', marginBottom: '10px' }}>{pred.crop || "Scanning..."}</div>
              
              <div className="ai-details">
                <p><b>Recommended Fertilizer</b> {pred.fertilizer || "Analyzing..."}</p>
                <p><b>Pathogen Analysis</b> {(pred.diseases || []).join(", ") || "No Risks Found"}</p>
              </div>
            </div>

            <div style={{ width: '220px', height: '160px', borderRadius: '16px', overflow: 'hidden', border: '1px solid var(--border)', background: '#fff', boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {pred.crop && !["Scanning...", "Awaiting Inputs", "Error"].includes(pred.crop) ? (
                <img 
                  src={`/crops/${pred.crop.toLowerCase().trim()}.png`} 
                  alt={pred.crop} 
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              ) : (
                <div style={{ textAlign: 'center', color: '#cbd5e1', padding: '20px' }}>
                  <div style={{ fontSize: '24px', marginBottom: '8px' }}>📡</div>
                  <div style={{ fontSize: '11px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Waiting for Data</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="stacked" style={{ gap: '30px' }}>
        <div className="glass-card">
          <h2>Geospatial Analysis</h2>
          <MapDisplay lat={pred.latitude} lon={pred.longitude} state={pred.state} />
          
          <div className="ai-details" style={{ marginTop: '24px', gridTemplateColumns: '1fr' }}>
            <p><b>Current Region</b> {pred.state || "India (General)"}</p>
            <div style={{ display: 'flex', gap: '20px', marginTop: '10px' }}>
              <p><b>Latitude</b> {pred.latitude || "20.59"}</p>
              <p><b>Longitude</b> {pred.longitude || "78.96"}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}