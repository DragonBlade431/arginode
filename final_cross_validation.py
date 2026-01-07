import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report, accuracy_score
from joblib import load

# Load dataset
df = pd.read_csv("data/arginode_corrected_fertilizers.csv")

X = df[['N','P','K','soil_ph','annual_rainfall_mm','avg_temp_c','soil_moisture_pct']]
y = df['crop'].astype(str)

model = load("models/crop_model.joblib")
scaler = load("models/scaler.joblib")
le = load("models/label_encoder.joblib")

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

accs = []
reports = []

for train_idx, test_idx in skf.split(X, y):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    X_train = scaler.transform(X_train)
    X_test = scaler.transform(X_test)

    y_pred_num = model.predict(X_test)
    y_pred = le.inverse_transform(y_pred_num)

    accs.append(accuracy_score(y_test, y_pred))
    reports.append(classification_report(y_test, y_pred, output_dict=True))

print("\nFold Accuracies:", [round(a*100,2) for a in accs])
print("Mean Accuracy:", round(np.mean(accs)*100, 2), "%")

macro_p = np.mean([r["macro avg"]["precision"] for r in reports])
macro_r = np.mean([r["macro avg"]["recall"] for r in reports])
macro_f = np.mean([r["macro avg"]["f1-score"] for r in reports])

print("\nMacro Precision:", round(macro_p*100,2), "%")
print("Macro Recall:", round(macro_r*100,2), "%")
print("Macro F1:", round(macro_f*100,2), "%")