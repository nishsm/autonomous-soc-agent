import pandas as pd
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)

    def fit(self, data: pd.DataFrame):
        self.model.fit(data)

    def predict(self, data: pd.DataFrame):
        preds = self.model.predict(data)
        return preds == -1  # True if anomaly
