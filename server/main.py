import time, json, asyncio, numpy as np
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from collections import deque
from server.geo_resolver import resolve_state

from server.models_loader import model_artifacts
from server.utils import get_disease_alerts

DB_FILE = Path("server/history.json")
if not DB_FILE.exists():
    DB_FILE.write_text("[]")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

buffer = deque(maxlen=12)
last_emit = 0
clients = set()
PAUSED = False

def stable_avg():
    return {k: round(np.mean([x[k] for x in buffer]), 2) for k in buffer[0]}

def save(row):
    db = json.loads(DB_FILE.read_text())
    db.insert(0, row)
    DB_FILE.write_text(json.dumps(db, indent=2))

# ================= AI CORE =================
def predict(d):
    X = [[
        d["N"], d["P"], d["K"],
        d["pH"], d["rainfall"],
        d["temperature"], d["humidity"]
    ]]

    X = model_artifacts["scaler"].transform(X)

    crop = model_artifacts["label_encoder"].inverse_transform(
        model_artifacts["crop_model"].predict(X)
    )[0]

    fertilizer = model_artifacts["fertilizer_recommender"].get_recommendation(d, crop)

    # 🔥 NEW — AUTO REGION DETECTION FROM GPS
    state = resolve_state(d.get("latitude",0), d.get("longitude",0))

    return {
        "crop": crop,
        "fertilizer": fertilizer,
        "state": state,
        "diseases": get_disease_alerts(crop)
    }
# ================= MANUAL =================
@app.post("/manual_predict")
async def manual(d: dict):
    for k in ["N","P","K","pH","temperature","humidity","rainfall"]:
        d[k] = float(d.get(k, 0))

    res = predict(d)

    row = {
        **res,
        "inputs": d,
        "field_type": "Manual Field",
        "timestamp": time.time()
    }
    save(row)
    return row

# ================= LIVE INGEST =================
@app.post("/ingest")
async def ingest(r: Request):
    global last_emit
    if PAUSED:
        return {"status": "paused"}
    
    d = await r.json()

    for k in ["N","P","K","pH","temperature","humidity","rainfall"]:
        d[k] = float(d.get(k, 0))

    buffer.append(d)
    if len(buffer) < 8:
        return {"status":"buffering"}

    stable = stable_avg()

    if time.time() - last_emit > 120:
        last_emit = time.time()
        res = predict(stable)
        row = {
            **res,
            "inputs": stable,
            "field_type": "Arduino Field",
            "timestamp": time.time()
        }
        save(row)
        await broadcast(row)

    return {"status":"ok"}

# ================= HISTORY =================
@app.get("/history")
def history():
    return json.loads(DB_FILE.read_text())

@app.delete("/history")
def clear():
    DB_FILE.write_text("[]")
    return {"status":"cleared"}

@app.get("/geojson")
def get_geojson():
    return json.loads(Path("data/india_states.geojson").read_text())

@app.post("/toggle_pause")
async def toggle_pause():
    global PAUSED
    PAUSED = not PAUSED
    return {"paused": PAUSED}

# ================= LIVE WS =================
@app.websocket("/ws/live")
async def ws(w: WebSocket):
    await w.accept()
    clients.add(w)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        clients.remove(w)

async def broadcast(row):
    for c in list(clients):
        try:
            await c.send_json(row)
        except:
            clients.remove(c)

# ================= RUN =================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)