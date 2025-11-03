# agents/siem_observer.py
import pandas as pd
import numpy as np
import joblib
import os

MODEL_PATH = "models/observer_model.pkl"
SCALER_PATH = "models/observer_scaler.pkl"

# Load model & scaler
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# Feature names that the model was trained on
TRAINED_FEATURES = joblib.load("models/trained_features.pkl")  # save this when training

def siem_observer(state):
    DATA_DIR = "data/synthetic_logs"

    csv_files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith(".csv")]

    logs_list = []
    for f in csv_files:
        try:
            print(f"📄 Reading {f}")
            df = pd.read_csv(f, low_memory=False)
            df.columns = [c.strip() for c in df.columns]
            logs_list.append(df)
        except Exception as e:
            print(f"⚠️ Skipping {f}: {e}")

    if not logs_list:
        state["logs"] = []
        state["suspicious"] = []
        return state

    logs = pd.concat(logs_list, ignore_index=True)
    print(f"✅ Loaded combined dataset shape: {logs.shape}")

    # Select only trained numeric features
    logs_numeric = logs.reindex(columns=TRAINED_FEATURES, fill_value=0)

    # Replace inf/-inf with NaN and fill
    logs_numeric.replace([np.inf, -np.inf], np.nan, inplace=True)
    logs_numeric.fillna(logs_numeric.mean(), inplace=True)

    # Scale and predict
    X = scaler.transform(logs_numeric)
    preds = model.predict(X)
    logs["is_suspicious"] = preds == -1

    suspicious = logs[logs["is_suspicious"]].to_dict(orient="records")
    print(f"🟡 [Observer] Suspicious logs detected: {len(suspicious)}")

    state["logs"] = logs.to_dict(orient="records")
    state["suspicious"] = suspicious

    return state
