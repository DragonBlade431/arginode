import pandas as pd
import numpy as np
import os

class CSVFertilizerRecommender:
    def __init__(self, csv_path):
        print("[FERTILIZER] Loading fertilizer CSV:", csv_path)
        self.df = pd.read_csv(csv_path)

        self.features = [
            "N","P","K",
            "soil_ph",
            "annual_rainfall_mm",
            "avg_temp_c",
            "soil_moisture_pct",
            "latitude",
            "longitude"
        ]

        print("[FERTILIZER] Using feature columns:", self.features)

    def get_recommendation(self, d, crop_name=None):

        v = np.array([
            d.get("N",0),
            d.get("P",0),
            d.get("K",0),
            d.get("pH",7),                     # map UI pH → soil_ph
            d.get("rainfall",0),               # UI rainfall → annual_rainfall_mm
            d.get("temperature",25),           # UI temp → avg_temp_c
            d.get("humidity",50),              # UI humidity → soil_moisture_pct
            d.get("latitude",0),
            d.get("longitude",0)
        ])

        A = self.df[self.features].values

        idx = np.linalg.norm(A - v, axis=1).argmin()
        return str(self.df.iloc[idx]["fertilizer_recommendation"])