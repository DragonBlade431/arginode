import React, { useState, useEffect, useCallback } from "react";
import LiveFeed from "./components/LiveFeed";
import StartPrediction from "./components/StartPrediction";
import History from "./components/History";
import "./components/LiveFeed.css";

export default function App() {
  const [tab, setTab] = useState("live");

  const [manualForm, setManualForm] = useState({ latitude: 13.165, longitude: 77.514 });
  const [manualResult, setManualResult] = useState({ state: "Karnataka (Detected)" });
  const [history, setHistory] = useState([]);

  // 🔒 Persistent Live State
  const [liveData, setLiveData] = useState({});
  const [livePred, setLivePred] = useState({ latitude: 13.165, longitude: 77.514, state: "Karnataka (Detected)" });

  useEffect(() => {
    fetch("http://127.0.0.1:8000/history")
      .then((r) => r.json())
      .then(setHistory);
  }, []);

  const handleStablePrediction = useCallback((p) => {
    setHistory((h) => [p, ...h]);
  }, []);

  return (
    <div className="app-root">
      <div className="app-header">
        <h1 className="main-title">
          <span className="title-line1" style={{ fontSize: '28px', textTransform: 'none' }}>
            Real-Time Offline Edge AI Framework
          </span>
          <span className="title-line2">
            For Sensor Integrated Precision Agriculture
          </span>
        </h1>

        <div className="nav-tabs">
          {["live", "manual", "history"].map((t) => (
            <button
              key={t}
              className={`nav-tab ${tab === t ? "active" : ""}`}
              onClick={() => setTab(t)}
            >
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="dashboard-wrapper">
        {tab === "live" && (
          <LiveFeed
            data={liveData}
            setData={setLiveData}
            pred={livePred}
            setPred={setLivePred}
          />
        )}

        {tab === "manual" && (
          <StartPrediction
            form={manualForm}
            setForm={setManualForm}
            result={manualResult}
            setResult={setManualResult}
          />
        )}

        {tab === "history" && <History history={history} />}
      </div>
    </div>
  );
}
