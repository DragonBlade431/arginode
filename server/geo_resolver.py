import pandas as pd
import numpy as np

df = pd.read_csv("data/arginode_corrected_fertilizers.csv")

def resolve_state(lat, lon):
    A = df[["latitude","longitude"]].values
    v = np.array([lat, lon])
    idx = np.linalg.norm(A - v, axis=1).argmin()
    return str(df.iloc[idx]["state"])