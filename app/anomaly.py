"""Runtime anomaly detection for transaction submissions."""

from __future__ import annotations

from sklearn.ensemble import IsolationForest


class TransactionAnomalyDetector:
    """Small Isolation Forest wrapper for runtime transaction behavior."""

    def __init__(self) -> None:
        self._model = IsolationForest(contamination=0.08, random_state=42)
        self._amounts = [1000, 5000, 10000, 25000, 100000, 250000, 500000]
        self._fit()

    def _fit(self) -> None:
        features = [[amount] for amount in self._amounts]
        self._model.fit(features)

    def add_amount(self, amount: float) -> None:
        self._amounts.append(float(amount))
        if len(self._amounts) >= 8:
            self._fit()

    def score(self, amount: float) -> dict[str, float | bool]:
        raw_score = float(self._model.decision_function([[float(amount)]])[0])
        is_anomaly = int(self._model.predict([[float(amount)]])[0]) == -1
        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": raw_score,
        }

