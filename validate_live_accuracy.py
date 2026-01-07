import numpy as np
from collections import Counter

def analyze(file):
    with open(file) as f:
        data = [x.strip() for x in f.readlines() if x.strip()]

    total = len(data)
    majority = Counter(data).most_common(1)[0]
    stability = (majority[1] / total) * 100

    print("\nFile:", file)
    print("Total readings:", total)
    print("Majority crop:", majority[0])
    print("Stability %:", round(stability,2))

analyze("soil_dry_clean.txt")
analyze("soil_normal_clean.txt")
analyze("soil_wet_clean.txt")
