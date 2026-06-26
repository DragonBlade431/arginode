import MapDisplay from "./MapDisplay";

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
        latitude: +form.latitude || 20.59,
        longitude: +form.longitude || 78.96,
      };

      const r = await fetch("http://127.0.0.1:8000/manual_predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const d = await r.json();
      setResult(d);
    } catch {
      setResult({ crop: "Error", fertilizer: "No Data", diseases: [] });
    }
  };

  const fields = [
    { k: "N", l: "Nitrogen" },
    { k: "P", l: "Phosphorus" },
    { k: "K", l: "Potassium" },
    { k: "pH", l: "Soil pH" },
    { k: "temperature", l: "Temp (°C)" },
    { k: "humidity", l: "Humidity (%)" },
    { k: "rainfall", l: "Rainfall (mm)" },
    { k: "latitude", l: "Latitude" },
    { k: "longitude", l: "Longitude" },
  ];

  return (
    <div className="dashboard-grid" style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '30px', width: '100%' }}>
      <div className="stacked" style={{ gap: '30px' }}>
        <div className="glass-card live-card">
          <div className="source-badge demo">Manual Entry</div>
          <h2>Crop Recommendation Engine</h2>

          <div className="sensor-grid">
            {fields.map(({ k, l }) => (
              <div key={k} className="sensor-box editable">
                <span className="sensor-label">{l}</span>
                <input
                  name={k}
                  type="number"
                  placeholder="0.0"
                  value={form[k] || ""}
                  onChange={change}
                />
              </div>
            ))}
          </div>

          <div className="ai-box" style={{ display: 'flex', gap: '30px', alignItems: 'center', minHeight: '180px' }}>
            <div style={{ flex: 1 }}>
              <div className="ai-label">Analysis Result</div>
              <div className="crop" style={{ fontSize: '32px', marginBottom: '10px' }}>{result.crop || "Awaiting Inputs"}</div>
              
              <div className="ai-details">
                <p><b>Recommended Fertilizer</b> {result.fertilizer || "---"}</p>
                <p><b>Pathogen Analysis</b> {(result.diseases || []).join(", ") || "---"}</p>
              </div>
            </div>

            <div style={{ width: '220px', height: '160px', borderRadius: '16px', overflow: 'hidden', border: '1px solid var(--border)', background: '#fff', boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {result.crop && !["Scanning...", "Awaiting Inputs", "Error"].includes(result.crop) ? (
                <img 
                  src={`/crops/${result.crop.toLowerCase().trim()}.png`} 
                  alt={result.crop} 
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              ) : (
                <div style={{ textAlign: 'center', color: '#cbd5e1', padding: '20px' }}>
                  <div style={{ fontSize: '24px', marginBottom: '8px' }}>🤖</div>
                  <div style={{ fontSize: '11px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Run Model to View</div>
                </div>
              )}
            </div>
          </div>

          <button className="predict-btn-full" onClick={submit}>
            Run Intelligence Model
          </button>
        </div>
      </div>

      <div className="stacked" style={{ gap: '30px' }}>
        <div className="glass-card">
          <h2>Location Context</h2>
          <MapDisplay lat={+form.latitude} lon={+form.longitude} state={result.state} />
          <div style={{ marginTop: '24px' }}>
            <p className="ai-label">Detected State</p>
            <p style={{ fontSize: '20px', fontWeight: '700' }}>{result.state || "India"}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
