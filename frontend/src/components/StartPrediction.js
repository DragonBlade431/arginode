import React from "react";
import "./LiveFeed.css";

export default function StartPrediction({ form, setForm, result, setResult }) {
  const change = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async () => {
    try {
      const payload = {
        N: +form.N || 0,
        P: +form.P || 0,
        K: +form.K || 0,
        pH: +form.pH || 7,
        temperature: +form.temperature || 25,
        humidity: +form.humidity || 50,
        rainfall: +form.rainfall || 0,
      };

      const r = await fetch("http://127.0.0.1:8000/manual_predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const d = await r.json();
      setResult(d);
    } catch {
      setResult({ crop: "ERROR", fertilizer: "ERROR", diseases: [] });
    }
  };

  return (
    <div className="glass-card live-card">
      <h2>🧪 Manual Crop Prediction</h2>

      <div className="sensor-grid">
        {["N", "P", "K", "pH", "temperature", "humidity", "rainfall"].map(
          (k) => (
            <div key={k} className="sensor-box editable">
              <span className="sensor-title">{k.toUpperCase()}</span>
              <input name={k} value={form[k] || ""} onChange={change} />
            </div>
          )
        )}
      </div>

      <div className="ai-box">
        <div className="crop">{result.crop || "--"}</div>
        <p>
          <b>Fertilizer:</b> {result.fertilizer || "--"}
        </p>
        <p>
          <b>Diseases:</b> {(result.diseases || []).join(", ") || "--"}
        </p>
      </div>

      <button className="predict-btn-full" onClick={submit}>
        🚀 Run AI Prediction
      </button>
    </div>
  );
}
