import React, { useEffect, useState } from "react";
import "./LiveFeed.css";

export default function History() {
  const [history, setHistory] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/history")
      .then((r) => r.json())
      .then(setHistory);
  }, []);

  const clearHistory = async () => {
    if (window.confirm("Are you sure you want to clear all history?")) {
      await fetch("http://127.0.0.1:8000/history", { method: "DELETE" });
      setHistory([]);
    }
  };

  return (
    <div className="history-section" style={{ width: '100%', maxWidth: '1000px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h2 style={{ margin: 0, fontSize: '24px' }}>Inference History</h2>
        <button
          onClick={clearHistory}
          style={{
            background: 'transparent',
            border: '1px solid #ef4444',
            color: '#ef4444',
            padding: '8px 16px',
            borderRadius: '8px',
            fontSize: '13px',
            fontWeight: '600',
            cursor: 'pointer'
          }}
        >
          Clear Logs
        </button>
      </div>

      <div className="history-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
        {history.map((h, i) => (
          <div key={i} className="glass-card" style={{ padding: '24px', minHeight: 'auto', cursor: 'pointer' }} onClick={() => setSelected(h)}>
            <div style={{ fontSize: '18px', fontWeight: '800', color: 'var(--primary)', marginBottom: '16px' }}>{h.crop}</div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Source</span>
                <span style={{ fontWeight: '600' }}>{h.field_type}</span>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Region</span>
                <span style={{ fontWeight: '600' }}>{h.state || "Unspecified"}</span>
              </div>
            </div>

            <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border)', fontSize: '11px', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
              <span>Click for details</span>
              <span>{new Date(h.timestamp * 1000).toLocaleTimeString()}</span>
            </div>
          </div>
        ))}
      </div>

      {/* DETAIL MODAL */}
      {selected && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="glass-card" style={{ maxWidth: '600px', width: '90%', position: 'relative' }}>
            <button onClick={() => setSelected(null)} style={{ position: 'absolute', top: '20px', right: '20px', background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer' }}>×</button>
            
            <h2 style={{ marginBottom: '10px' }}>Prediction Analysis</h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: '30px' }}>{new Date(selected.timestamp * 1000).toLocaleString()}</p>

            <div style={{ display: 'flex', gap: '30px', alignItems: 'center', background: '#f8fafc', padding: '24px', borderRadius: '16px', marginBottom: '30px' }}>
              <div style={{ flex: 1 }}>
                <div className="ai-label">Recommended Crop</div>
                <div style={{ fontSize: '32px', fontWeight: '800', color: 'var(--primary)' }}>{selected.crop}</div>
              </div>
              
              <div style={{ width: '160px', height: '120px', borderRadius: '12px', overflow: 'hidden', border: '1px solid var(--border)', background: '#fff' }}>
                <img 
                  src={`/crops/${selected.crop.toLowerCase().trim()}.png`} 
                  alt={selected.crop} 
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  onError={(e) => e.target.style.display = 'none'}
                />
              </div>
            </div>

            <div className="sensor-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', gap: '15px' }}>
              {Object.entries(selected.inputs || {}).map(([k, v]) => (
                <div key={k} style={{ background: '#fff', border: '1px solid var(--border)', padding: '12px', borderRadius: '8px' }}>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: '700', textTransform: 'uppercase' }}>{k}</div>
                  <div style={{ fontSize: '16px', fontWeight: '700' }}>{v}</div>
                </div>
              ))}
            </div>

            <div style={{ marginTop: '30px', paddingTop: '20px', borderTop: '1px solid var(--border)' }}>
              <p style={{ marginBottom: '10px' }}><b>Fertilizer:</b> {selected.fertilizer}</p>
              <p><b>Diseases:</b> {(selected.diseases || []).join(", ") || "None detected"}</p>
            </div>
          </div>
        </div>
      )}

      {history.length === 0 && (
        <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-muted)', border: '2px dashed var(--border)', borderRadius: '24px' }}>
          No historical records found.
        </div>
      )}
    </div>
  );
}
