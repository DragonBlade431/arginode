import serial
import time
import numpy as np
import joblib
import json
from server.utils import get_disease_alerts

PORT = "/dev/tty.usbserial-3140"
BAUD = 9600

print("\n🌱 LIVE SMART AGRICULTURE AI SYSTEM READY\n")

model = joblib.load("models/crop_model.joblib")
scaler = joblib.load("models/scaler.joblib")
le = joblib.load("models/label_encoder.joblib")
fert = json.load(open("models/fertilizer_map.json"))

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

buffer = []

def safe(v, low, high, default):
    try:
        v = float(v)
        if low <= v <= high:
            return v
    except:
        pass
    print("⚠️ Sensor noise auto-recovered")
    return default

while True:
    try:
        line = ser.readline().decode(errors="ignore").strip().lower()

        if "*start*" in line:
            data = {}
            for _ in range(9):
                l = ser.readline().decode(errors="ignore").strip().lower()
                if ":" in l:
                    k, v = l.replace("*","").split(":")
                    data[k.strip()] = v.strip()

            N    = safe(data.get("n"),   0, 500, 100)
            P    = safe(data.get("p"),   0, 500, 100)
            K    = safe(data.get("k"),   0, 500, 100)
            ph   = safe(data.get("ph"),  3, 10,  7)
            temp = safe(data.get("t"),  10, 50, 25)
            soil = safe(data.get("s"),   0, 100, 40)

            X = np.array([[N, P, K, ph, 0, temp, soil]])
            Xs = scaler.transform(X)

            pred = model.predict(Xs)[0]
            buffer.append(pred)
            if len(buffer) > 5:
                buffer.pop(0)

            final_pred = max(set(buffer), key=buffer.count)
            crop = le.inverse_transform([final_pred])[0]
            prob = max(model.predict_proba(Xs)[0])

            print("====================================")
            print("🌾 Crop:", crop)
            print("🎯 Confidence:", round(prob*100,2), "%")
            print("💊 Fertilizer:", fert.get(crop.lower()))
            print("⚠️ Diseases:", get_disease_alerts(crop))
            print("====================================\n")

    except Exception as e:
        print("⚠️ Serial stream waiting…")
