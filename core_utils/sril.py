import numpy as np
from collections import deque

class SRIL:
    def __init__(self):
        self.window = deque(maxlen=5)
        self.medians = {
            'N': 90, 'P': 42, 'K': 43,
            'soil_ph': 6.5,
            'annual_rainfall_mm': 1100,
            'avg_temp_c': 27,
            'soil_moisture_pct': 45
        }
        self.last_preds = deque(maxlen=3)

    def sanitize(self, data):
        # Missing value recovery
        for k in self.medians:
            if k not in data or data[k] is None:
                data[k] = self.medians[k]

        # Anomaly rejection
        if not (3 <= data['soil_ph'] <= 10): data['soil_ph'] = self.medians['soil_ph']
        if not (0 <= data['N'] <= 200): data['N'] = self.medians['N']
        if not (0 <= data['P'] <= 200): data['P'] = self.medians['P']
        if not (0 <= data['K'] <= 200): data['K'] = self.medians['K']
        if not (0 <= data['soil_moisture_pct'] <= 100): data['soil_moisture_pct'] = self.medians['soil_moisture_pct']

        self.window.append([data[k] for k in self.medians])
        smooth = np.mean(self.window, axis=0)

        return dict(zip(self.medians.keys(), smooth))

    def stabilize(self, pred):
        self.last_preds.append(pred)
        return max(set(self.last_preds), key=self.last_preds.count)