"""anomaly_detection — Isolation Forest, LOF, rolling z-score anomaly detection."""

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class AnomalyResult:
    labels: np.ndarray  # -1 = anomaly, 1 = normal
    scores: np.ndarray
    n_anomalies: int
    anomaly_pct: float
    anomaly_indices: list


def fit_isolation_forest(
    X: np.ndarray | pd.DataFrame,
    contamination: float = 0.05,
    random_state: int = 42,
) -> AnomalyResult:
    """Isolation Forest anomaly detection."""
    from sklearn.ensemble import IsolationForest

    X_arr = np.asarray(X)
    if X_arr.ndim == 1:
        X_arr = X_arr.reshape(-1, 1)

    ifo = IsolationForest(contamination=contamination, random_state=random_state, n_estimators=200)
    labels = ifo.fit_predict(X_arr)
    scores = ifo.decision_function(X_arr)
    idx = np.where(labels == -1)[0].tolist()

    return AnomalyResult(
        labels=labels, scores=scores, n_anomalies=len(idx),
        anomaly_pct=len(idx) / len(X_arr) * 100, anomaly_indices=idx,
    )


def fit_lof(
    X: np.ndarray | pd.DataFrame,
    n_neighbors: int = 20,
    contamination: float = 0.05,
) -> AnomalyResult:
    """Local Outlier Factor."""
    from sklearn.neighbors import LocalOutlierFactor

    X_arr = np.asarray(X)
    if X_arr.ndim == 1:
        X_arr = X_arr.reshape(-1, 1)

    lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=contamination)
    labels = lof.fit_predict(X_arr)
    scores = lof.negative_outlier_factor_
    idx = np.where(labels == -1)[0].tolist()

    return AnomalyResult(
        labels=labels, scores=scores, n_anomalies=len(idx),
        anomaly_pct=len(idx) / len(X_arr) * 100, anomaly_indices=idx,
    )


def rolling_anomaly(
    series: pd.Series,
    window: int = 60,
    threshold: float = 3.0,
) -> pd.Series:
    """Rolling z-score anomaly flags. Returns boolean Series."""
    mu = series.rolling(window).mean()
    sigma = series.rolling(window).std()
    z = (series - mu) / sigma
    return (z.abs() > threshold).rename("anomaly")


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    data = rng.normal(size=500)
    data[100] = 10  # inject anomaly
    data[300] = -8

    result = fit_isolation_forest(data, contamination=0.02)
    print(f"Anomalies: {result.n_anomalies} ({result.anomaly_pct:.1f}%)")
    print(f"Indices: {result.anomaly_indices[:10]}")
