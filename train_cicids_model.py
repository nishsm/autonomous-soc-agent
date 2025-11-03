"""
train_cicids_model.py
Train an Isolation Forest anomaly detector using multiple CICIDS2017 CSV files.
"""

import pandas as pd
import numpy as np
import joblib
import os
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, roc_auc_score
from glob import glob

# ----------------------------
# Config
# ----------------------------
DATA_DIR = "data/cicids2017"
MODEL_OUT = "models/isolation_forest.joblib"
SCALER_OUT = "models/scaler.joblib"
SUSPICIOUS_OUT = "data/suspicious_sample.csv"

os.makedirs("models", exist_ok=True)

# ----------------------------
# Load all CSVs
# ----------------------------
print(f"🔹 Loading all CSVs from {DATA_DIR} ...")

csv_files = glob(os.path.join(DATA_DIR, "*.csv"))
if not csv_files:
    raise FileNotFoundError(f"No CSV files found in {DATA_DIR}")

dfs = []
for f in csv_files:
    try:
        print(f"📄 Reading {f} ...")
        df = pd.read_csv(f, low_memory=False)
        df.columns = [c.strip() for c in df.columns]
        dfs.append(df)
    except Exception as e:
        print(f"⚠️ Skipping {f} due to read error: {e}")

df = pd.concat(dfs, ignore_index=True)
print(f"✅ Combined dataset shape: {df.shape}")

# ----------------------------
# Basic cleaning
# ----------------------------
df = df.dropna(subset=["Flow Duration", "Total Fwd Packets", "Total Backward Packets"], how="any")

# ----------------------------
# Feature selection
# ----------------------------
numeric_features = [
    "Flow Duration", "Total Fwd Packets", "Total Backward Packets",
    "Total Length of Fwd Packets", "Total Length of Bwd Packets",
    "Fwd Packet Length Max", "Fwd Packet Length Min", "Fwd Packet Length Mean", "Fwd Packet Length Std",
    "Bwd Packet Length Max", "Bwd Packet Length Min", "Bwd Packet Length Mean", "Bwd Packet Length Std",
    "Flow Bytes/s", "Flow Packets/s", "Flow IAT Mean", "Flow IAT Std", "Flow IAT Max", "Flow IAT Min",
    "Fwd IAT Total", "Fwd IAT Mean", "Fwd IAT Std", "Fwd IAT Max", "Fwd IAT Min",
    "Bwd IAT Total", "Bwd IAT Mean", "Bwd IAT Std", "Bwd IAT Max", "Bwd IAT Min",
    "Fwd Header Length", "Bwd Header Length",
    "Min Packet Length", "Max Packet Length", "Packet Length Mean", "Packet Length Std", "Packet Length Variance",
    "Average Packet Size", "Avg Fwd Segment Size", "Avg Bwd Segment Size",
    "Active Mean", "Active Std", "Active Max", "Active Min",
    "Idle Mean", "Idle Std", "Idle Max", "Idle Min"
]

numeric_features = [f for f in numeric_features if f in df.columns]
print(f"✅ Using {len(numeric_features)} numeric features")

# ----------------------------
# Label handling
# ----------------------------
if "Label" not in df.columns:
    raise ValueError("❌ Dataset missing 'Label' column — required for evaluation.")

df["is_attack"] = df["Label"].apply(lambda x: 0 if "BENIGN" in str(x).upper() else 1)

# ----------------------------
# Train/test split
# ----------------------------
train_df = df.sample(frac=0.7, random_state=42)
test_df = df.drop(train_df.index)

# ----------------------------
# Clean data — handle inf, NaN, extreme values
# ----------------------------
def clean_numeric_data(df, feature_list):
    """Replace inf/NaN and clip extreme values."""
    # Identify problematic columns
    cols_with_inf = df[feature_list].columns[np.isinf(df[feature_list].to_numpy()).any(axis=0)].tolist()
    if cols_with_inf:
        print(f"⚠️ Columns containing inf/-inf: {cols_with_inf}")

    # Replace and clean
    df[feature_list] = df[feature_list].replace([np.inf, -np.inf], np.nan)
    before_rows = df.shape[0]
    df = df.dropna(subset=feature_list)
    after_rows = df.shape[0]
    print(f"🧹 Dropped {before_rows - after_rows} rows with NaN or inf")

    # Clip extreme outliers (helps prevent float overflow)
    df[feature_list] = df[feature_list].clip(lower=-1e10, upper=1e10)
    return df

train_df = clean_numeric_data(train_df, numeric_features)
test_df = clean_numeric_data(test_df, numeric_features)

print(f"✅ After cleaning: {train_df.shape[0]} training samples, {test_df.shape[0]} test samples")

# ----------------------------
# Scale features
# ----------------------------
scaler = StandardScaler()
X_train = scaler.fit_transform(train_df[numeric_features])
X_test = scaler.transform(test_df[numeric_features])
y_test = test_df["is_attack"].values

# ----------------------------
# Train model
# ----------------------------
print("🚀 Training Isolation Forest ...")
model = IsolationForest(
    n_estimators=200,
    contamination=0.01,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train)

# ----------------------------
# Evaluate model
# ----------------------------
scores = -model.decision_function(X_test)
preds = model.predict(X_test)
preds = np.where(preds == -1, 1, 0)

try:
    auc = roc_auc_score(y_test, scores)
    print(f"🎯 ROC-AUC: {auc:.4f}")
except Exception:
    print("⚠️ ROC-AUC computation failed.")
    auc = None

print("\n📊 Classification Report:")
print(classification_report(y_test, preds, digits=3))

# ----------------------------
# Save models
# ----------------------------
joblib.dump(model, MODEL_OUT)
joblib.dump(scaler, SCALER_OUT)
print(f"💾 Saved model → {MODEL_OUT}")
print(f"💾 Saved scaler → {SCALER_OUT}")

# ----------------------------
# Extract suspicious samples
# ----------------------------
test_df = test_df.copy()
test_df["anomaly_score"] = scores
test_df["predicted_anomaly"] = preds

suspicious_df = test_df[test_df["predicted_anomaly"] == 1].sort_values(by="anomaly_score", ascending=False)
suspicious_df.head(100).to_csv(SUSPICIOUS_OUT, index=False)
print(f"📁 Exported top 100 suspicious flows → {SUSPICIOUS_OUT}")

print(f"✅ Training complete. Total suspicious flows detected: {len(suspicious_df)}")

import joblib
import os

os.makedirs("models", exist_ok=True)

joblib.dump(model, "models/observer_model.pkl")
joblib.dump(scaler, "models/observer_scaler.pkl")

print("💾 Saved model and scaler to 'models/'")

# Save numeric features used for training
import joblib
joblib.dump(numeric_features, "models/trained_features.pkl")
print(f"💾 Saved trained feature list → models/trained_features.pkl")
