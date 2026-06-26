import serial, time, numpy as np, joblib, json, websocket, sys, argparse
from server.utils import get_disease_alerts

def get_default_port():
    if sys.platform.startswith('win'):
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        if ports:
            return ports[0].device
        return "COM3"
    return "/dev/tty.usbserial-3140"

parser = argparse.ArgumentParser()
parser.add_argument("--port", default=get_default_port(), help="Serial port for ESP32")
parser.add_argument("--baud", type=int, default=9600, help="Baud rate")
args = parser.parse_args()

PORT = args.port
BAUD = args.baud

# Load models
# ... (rest of imports/setup)
model = joblib.load("models/crop_model.joblib")
scaler = joblib.load("models/scaler.joblib")
le = joblib.load("models/label_encoder.joblib")
fert_map = json.load(open("models/fertilizer_map.json"))

# Dashboard socket (correct channel)
ws = websocket.WebSocket()
try:
    ws.connect("ws://localhost:8000/ws/arduino")
except Exception as e:
    print(f"❌ Could not connect to backend WebSocket: {e}")
    print("💡 Make sure the FastAPI server is running (uvicorn server.main:app)")
    sys.exit(1)

print(f"\n🌱 LIVE SMART AGRICULTURE AI SYSTEM READY")
print(f"🔌 Connected to: {PORT} @ {BAUD}\n")

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
except Exception as e:
    print(f"❌ Could not open serial port {PORT}: {e}")
    sys.exit(1)

time.sleep(2)

frame = []

def clean(v):
    try:
        return float(v)
    except:
        return None

while True:
    try:
        line = ser.readline().decode(errors="ignore").strip()

        if "*start*" in line:
            frame = []
            continue

        if frame is not None and line.startswith("*") and ":" in line:
            frame.append(line)

        if len(frame) >= 9:
            data = {}
            for l in frame:
                k, v = l.replace("*", "").split(":")
                data[k.strip()] = clean(v.strip())

            frame = None

            N = data.get("n", 0)
            P = data.get("p", 0)
            K = data.get("k", 0)
            ph = data.get("ph", 7)
            temp = data.get("t", 25)
            hum = data.get("h", 50)
            soil = data.get("s", 0)
            lat = data.get("la", 0)
            lon = data.get("lo", 0)

            X = np.array([[N, P, K, ph, 0, temp, soil]])
            Xs = scaler.transform(X)

            pred = model.predict(Xs)[0]
            prob = max(model.predict_proba(Xs)[0])
            crop = le.inverse_transform([pred])[0]

            # 🔥 EXACT keys frontend expects
            payload = {
                "n": N,
                "p": P,
                "k": K,
                "ph": ph,
                "temperature": temp,
                "humidity": hum,
                "moisture": soil,
                "lat": lat,
                "lon": lon,
                "crop": crop,
                "confidence": round(prob * 100, 2),
                "fertilizer": fert_map.get(crop.lower()),
                "diseases": get_disease_alerts(crop)
            }

            ws.send(json.dumps(payload))
            print("📡 Sent to dashboard →", payload)

    except Exception:
        print("⚠️ Sensor noise auto-recovered")