# server/utils.py

import json
from core_utils.area_utils import calculate_area_acres


# ------------------------------------------------------------------
# Disease Advisory Rules (Offline Rule Engine)
# ------------------------------------------------------------------

def get_disease_alerts(crop_name):
    alerts = {
        "rice": ["Blast", "Brown Spot"],
        "wheat": ["Rust", "Loose Smut"],
        "maize": ["Fall Armyworm", "Leaf Blight"],
        "cotton": ["Bollworm", "Wilt"],
        "sugarcane": ["Red Rot", "Sugarcane Smut"],
        "banana": ["Panama Disease", "Sigatoka Leaf Spot"],
        "potato": ["Late Blight", "Common Scab"],
        "pulses": ["Yellow Mosaic Virus"],
        "tea": ["Blister Blight"],
        "coffee": ["Coffee Leaf Rust"],
        "jute": ["Stem Rot"],
        "mulberry": ["Powdery Mildew"],
        "coconut": ["Bud Rot"]
    }

    return alerts.get((crop_name or "").lower(), ["No major disease risks detected"])


# ------------------------------------------------------------------
# Fertilizer Recommendation Engine
# ------------------------------------------------------------------

class FertilizerRecommender:
    """
    Hybrid fertilizer advisory engine:
    1. Dataset-driven JSON lookup (primary)
    2. ML fallback (optional)
    3. Safe offline default
    """

    def __init__(self, fertilizer_map, fertilizer_model_artifacts=None):
        self.fertilizer_map = fertilizer_map
        self.fertilizer_model_artifacts = fertilizer_model_artifacts

    def recommend(self, crop_name, features=None):
        lookup = (crop_name or "").lower()

        # 1️⃣ Dataset JSON Lookup (Primary Offline Layer)
        if self.fertilizer_map:
            rec = self.fertilizer_map.get(lookup)
            if rec:
                return rec

        # 2️⃣ ML-based Fallback (Optional Layer)
        if self.fertilizer_model_artifacts and features is not None:
            try:
                model = self.fertilizer_model_artifacts["model"]
                scaler = self.fertilizer_model_artifacts["scaler"]
                le = self.fertilizer_model_artifacts["label_encoder"]

                features_2d = features.reshape(1, -1)
                scaled = scaler.transform(features_2d)
                pred_numeric = model.predict(scaled)
                return le.inverse_transform(pred_numeric)[0]
            except Exception as e:
                print(f"[ERROR] Fertilizer ML fallback failed → {e}")

        # 3️⃣ Safe Default
        return f"Normal fertilizers needed for {crop_name}."


# ------------------------------------------------------------------
# Geo-Spatial Utilities (Used by Frontend)
# ------------------------------------------------------------------

def calculate_field_area_acres(polygon_points):
    try:
        return round(calculate_area_acres(polygon_points), 2)
    except:
        return 0.0