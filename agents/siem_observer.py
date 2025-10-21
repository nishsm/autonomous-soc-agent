import pandas as pd
from models.anomaly_detector import AnomalyDetector

def siem_observer(state):
    """Collects logs and detects anomalies using Isolation Forest."""
    logs = pd.DataFrame([
        {"user": "alice", "login_attempts": 5, "files_accessed": 2},
        {"user": "bob", "login_attempts": 1, "files_accessed": 1},
        {"user": "eve", "login_attempts": 10, "files_accessed": 9}
    ])
    model = AnomalyDetector()
    model.fit(logs[["login_attempts", "files_accessed"]])
    logs["is_suspicious"] = model.predict(logs[["login_attempts", "files_accessed"]])

    suspicious = logs[logs["is_suspicious"]].to_dict(orient="records")
    print("🟡 [Observer] Suspicious logs:", suspicious)
    return {"logs": logs.to_dict(orient="records"), "suspicious": suspicious}
