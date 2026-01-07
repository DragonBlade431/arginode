import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from joblib import load

df = pd.read_csv("data/arginode_corrected_fertilizers.csv")

X = df[['N','P','K','soil_ph','annual_rainfall_mm','avg_temp_c','soil_moisture_pct']]
y = df['crop'].astype(str)

model = load("models/crop_model.joblib")
scaler = load("models/scaler.joblib")
encoder = load("models/label_encoder.joblib")

X = scaler.transform(X)
y_enc = encoder.transform(y)
y_pred_enc = model.predict(X)
y_pred = encoder.inverse_transform(y_pred_enc)

labels = sorted(y.unique())

cm = confusion_matrix(y, y_pred, labels=labels)
cm = cm / cm.sum(axis=1, keepdims=True) * 100

plt.figure(figsize=(6.4,5))
plt.imshow(cm, cmap="Blues")
plt.colorbar(label="%")
plt.xticks(range(len(labels)), labels, rotation=90)
plt.yticks(range(len(labels)), labels)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Normalized Confusion Matrix (%)")

for i in range(len(labels)):
    plt.text(i,i,f"{cm[i,i]:.1f}",ha="center",va="center",color="white",fontsize=7)

plt.tight_layout()
plt.savefig("ieee_confusion_matrix.png", dpi=300)
plt.close()

table = pd.read_csv("ieee_classification_table.csv")
table = table[table['Unnamed: 0']!='accuracy']

plt.figure(figsize=(6.4,4))
plt.bar(table['Unnamed: 0'], table['f1-score']*100)
plt.xticks(rotation=90)
plt.ylabel("F1 Score (%)")
plt.ylim(85,100)
plt.title("Per-Crop F1 Score")
plt.tight_layout()
plt.savefig("ieee_f1_scores.png", dpi=300)
plt.close()

print("IEEE figures generated.")