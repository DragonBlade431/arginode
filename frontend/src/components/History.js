import React, { useEffect, useState } from "react";
import "./LiveFeed.css";

export default function History() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/history")
      .then((r) => r.json())
      .then(setHistory);
  }, []);

  return (
    <div className="history-section">
      <h2 className="history-heading">📜 Prediction History</h2>

      <button
        onClick={async () => {
          await fetch("http://127.0.0.1:8000/history", { method: "DELETE" });
          setHistory([]);
        }}
        className="clear-history-btn"
      >
        🗑 Clear All History
      </button>

      <div className="history-grid">
        {history.map((h, i) => (
          <div key={i} className="history-tile">
            <div className="tile-crop">{h.crop}</div>

            <div className="tile-row">
              <span>Field</span>
              <span className="field-pill">{h.field_type}</span>
            </div>

            {/* ✅ Region (from live Arduino GPS or manual dataset) */}
            {h.state && (
              <div className="tile-row">
                <span>Region</span>
                <span>{h.state}</span>
              </div>
            )}

            <div className="tile-row">
              <span>Fertilizer</span>
              <span>{h.fertilizer}</span>
            </div>

            <div className="tile-row">
              <span>Diseases</span>
              <span>{(h.diseases || []).join(", ")}</span>
            </div>

            <div className="tile-time">
              {new Date(h.timestamp * 1000).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
