import pandas as pd
from joblib import load
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report

df = pd.read_csv("data/arginode_corrected_fertilizers.csv")

X = df[['N','P','K','soil_ph','annual_rainfall_mm','avg_temp_c','soil_moisture_pct']]
y = df['crop'].astype(str)

model = load("models/crop_model.joblib")
scaler = load("models/scaler.joblib")
encoder = load("models/label_encoder.joblib")   # <—— THIS

X = scaler.transform(X)
y_enc = encoder.transform(y)                     # <—— FIX

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y_enc, cv=cv)

print("\nCross-Validation Accuracy:", scores.mean())

y_pred = model.predict(X)
y_pred_lbl = encoder.inverse_transform(y_pred)

report = classification_report(y, y_pred_lbl, output_dict=True)
pd.DataFrame(report).T.to_csv("ieee_classification_table.csv")

print("Classification table saved.")