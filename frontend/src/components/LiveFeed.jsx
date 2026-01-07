import React, { useEffect } from "react";
import "./LiveFeed.css";

export default function LiveFeed({ data, setData, pred, setPred }) {

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

  return (
    <div className="glass-card live-card">
      <h2>🌱 Real-Time Agricultural AI Dashboard</h2>

      <div className="sensor-grid">
        {[
          { k: "N", u: "mg/kg" },
          { k: "P", u: "mg/kg" },
          { k: "K", u: "mg/kg" },
          { k: "pH" },
          { k: "temperature", l: "TEMP", u: "°C" },
          { k: "humidity", l: "HUMIDITY", u: "%" },
          { k: "rainfall", l: "RAINFALL", u: "mm" },
        ].map(({ k, l, u }) => (
          <div key={k} className="sensor-box stacked">
            <span className="sensor-label">{l || k}</span>
            <span className="sensor-value">{data?.[k] ?? "--"}</span>
            {u && <span className="sensor-unit">{u}</span>}
          </div>
        ))}
      </div>

      <div className="ai-box">
        <div className="crop">{pred.crop || "--"}</div>
        <p><b>Fertilizer:</b> {pred.fertilizer || "--"}</p>
        <p><b>Diseases:</b> {(pred.diseases || []).join(", ") || "--"}</p>
        <p className="region">
  {pred.state ? `📍 ${pred.state}` : pred.field_type || "Live Field"}
</p>
      </div>
    </div>
  );
}