"""
generate_synthetic_logs.py
Generate synthetic network logs with injected anomalies for testing the SOC pipeline.
"""

import pandas as pd
import numpy as np
import os

# ----------------------------
# Config
# ----------------------------
OUT_DIR = "data/synthetic_logs"
os.makedirs(OUT_DIR, exist_ok=True)
OUT_FILE = os.path.join(OUT_DIR, "synthetic_logs.csv")

N_ROWS = 100  # total rows
ANOMALY_FRACTION = 0.02  # fraction of anomalies

# ----------------------------
# Define feature ranges (approx. based on CICIDS)
# ----------------------------
feature_ranges = {
    "Flow Duration": (100, 5000),
    "Total Fwd Packets": (1, 50),
    "Total Backward Packets": (1, 50),
    "Total Length of Fwd Packets": (40, 50000),
    "Total Length of Bwd Packets": (40, 50000),
    "Fwd Packet Length Max": (40, 1500),
    "Fwd Packet Length Min": (40, 1500),
    "Fwd Packet Length Mean": (40, 1500),
    "Fwd Packet Length Std": (0, 200),
    "Bwd Packet Length Max": (40, 1500),
    "Bwd Packet Length Min": (40, 1500),
    "Bwd Packet Length Mean": (40, 1500),
    "Bwd Packet Length Std": (0, 200),
    "Flow Bytes/s": (100, 1_000_000),
    "Flow Packets/s": (1, 1000),
    "Flow IAT Mean": (0, 1000),
    "Flow IAT Std": (0, 500),
    "Flow IAT Max": (0, 5000),
    "Flow IAT Min": (0, 500),
    "Fwd IAT Total": (0, 100_000),
    "Fwd IAT Mean": (0, 1000),
    "Fwd IAT Std": (0, 500),
    "Fwd IAT Max": (0, 5000),
    "Fwd IAT Min": (0, 500),
    "Bwd IAT Total": (0, 100_000),
    "Bwd IAT Mean": (0, 1000),
    "Bwd IAT Std": (0, 500),
    "Bwd IAT Max": (0, 5000),
    "Bwd IAT Min": (0, 500),
    "Fwd Header Length": (20, 60),
    "Bwd Header Length": (20, 60),
    "Min Packet Length": (40, 1500),
    "Max Packet Length": (40, 1500),
    "Packet Length Mean": (40, 1500),
    "Packet Length Std": (0, 200),
    "Packet Length Variance": (0, 40000),
    "Average Packet Size": (40, 1500),
    "Avg Fwd Segment Size": (40, 1500),
    "Avg Bwd Segment Size": (40, 1500),
    "Active Mean": (0, 5000),
    "Active Std": (0, 2000),
    "Active Max": (0, 10000),
    "Active Min": (0, 1000),
    "Idle Mean": (0, 5000),
    "Idle Std": (0, 2000),
    "Idle Max": (0, 10000),
    "Idle Min": (0, 1000),
}

# ----------------------------
# Generate synthetic normal data
# ----------------------------
data = {}
for feature, (low, high) in feature_ranges.items():
    data[feature] = np.random.randint(low, high + 1, N_ROWS)

df = pd.DataFrame(data)

# ----------------------------
# Inject anomalies
# ----------------------------
n_anomalies = int(N_ROWS * ANOMALY_FRACTION)
anomaly_indices = np.random.choice(N_ROWS, n_anomalies, replace=False)

for feature in feature_ranges.keys():
    # anomalies are extreme values outside normal range
    df.loc[anomaly_indices, feature] = df.loc[anomaly_indices, feature] * 10

df["Label"] = "BENIGN"
df.loc[anomaly_indices, "Label"] = "ANOMALY"

# Optional: add fake users for planner
users = [f"user{i}" for i in range(1, 21)]
df["user"] = np.random.choice(users, N_ROWS)

# ----------------------------
# Save to CSV
# ----------------------------
df.to_csv(OUT_FILE, index=False)
print(f"✅ Synthetic logs saved to {OUT_FILE}")
print(f"Total rows: {N_ROWS}, Anomalies injected: {n_anomalies}")
