# predict_local.py
"""
Fault-Tolerant Offline Prediction Engine
(Research-grade, IEEE-ready)

Adds:
• Noise filtering
• Missing value recovery
• Prediction stabilization
"""

import joblib
import json
import numpy as np
import argparse
import os
import sys
from collections import deque

# Import the rule-based alerts
from server.utils import get_disease_alerts

MODELS_DIR = "models"
CROP_MODEL_PATH = os.path.join(MODELS_DIR, "crop_model.joblib")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.joblib")
LABEL_ENCODER_PATH = os.path.join(MODELS_DIR, "label_encoder.joblib")
FERTILIZER_MAP_PATH = os.path.join(MODELS_DIR, "fertilizer_map.json")

FEATURES = ['N','P','K','soil_ph','annual_rainfall_mm','avg_temp_c','soil_moisture_pct']

# ---------- Sensor Reliability & Intelligence Layer (SRIL) ----------
class SRIL:
    def __init__(self):
        self.window = deque(maxlen=5)
        self.last_preds = deque(maxlen=3)
        self.defaults = {
            'N': 90, 'P': 42, 'K': 43,
            'soil_ph': 6.5,
            'annual_rainfall_mm': 1100,
            'avg_temp_c': 27,
            'soil_moisture_pct': 45
        }

    def sanitize(self, raw):
        clean = {}
        for k in FEATURES:
            val = raw.get(k)
            if val is None or not np.isfinite(val):
                val = self.defaults[k]
            clean[k] = val

        if not (3 <= clean['soil_ph'] <= 10): clean['soil_ph'] = self.defaults['soil_ph']
        if not (0 <= clean['soil_moisture_pct'] <= 100): clean['soil_moisture_pct'] = self.defaults['soil_moisture_pct']

        self.window.append([clean[k] for k in FEATURES])
        smooth = np.mean(self.window, axis=0)
        return dict(zip(FEATURES, smooth))

    def stabilize(self, pred):
        self.last_preds.append(pred)
        return max(set(self.last_preds), key=self.last_preds.count)

sril = SRIL()

# ------------------ Load Models ------------------
def load_artifacts():
    model = joblib.load(CROP_MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    label_encoder = joblib.load(LABEL_ENCODER_PATH)
    with open(FERTILIZER_MAP_PATH) as f:
        fertilizer_map = json.load(f)
    return model, scaler, label_encoder, fertilizer_map

# ------------------ Prediction ------------------
def predict(clean_dict, model, scaler, label_encoder):
    X = np.array([[clean_dict[f] for f in FEATURES]])
    Xs = scaler.transform(X)
    pred = model.predict(Xs)[0]
    proba = model.predict_proba(Xs)
    confidence = float(np.max(proba))
    crop = label_encoder.inverse_transform([pred])[0]
    return crop, confidence

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-row", required=True)
    args = parser.parse_args()

    model, scaler, encoder, fertilizer_map = load_artifacts()

    values = [float(v) for v in args.input_row.split(',')]
    raw = dict(zip(FEATURES, values))

    clean = sril.sanitize(raw)
    crop, conf = predict(clean, model, scaler, encoder)
    final_crop = sril.stabilize(crop)

    fertilizer = fertilizer_map.get(final_crop.lower(), "No recommendation")
    disease = get_disease_alerts(final_crop)

    print("\n--- 🌱 Smart Agriculture AI ---")
    print("Predicted Crop:", final_crop)
    print("Confidence:", f"{conf*100:.2f}%")
    print("Fertilizer:", fertilizer)
    print("Disease Alerts:", ", ".join(disease))
    print("-------------------------------\n")

if __name__ == "__main__":
    main()