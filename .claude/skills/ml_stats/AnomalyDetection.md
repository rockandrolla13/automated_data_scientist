# AnomalyDetection

## When to Use
- Detecting unusual spread moves, volume spikes, or return outliers.
- Surveillance: flagging data quality issues or regime shifts.
- Unsupervised: no labeled anomalies needed.

## Packages
```python
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.covariance import EllipticEnvelope
```

## Corresponding Script
`/scripts/ml_stats/anomaly_detection.py`
- `fit_isolation_forest(X, contamination) -> AnomalyResult`
- `fit_lof(X, n_neighbors, contamination) -> AnomalyResult`
- `rolling_anomaly(series, window, threshold) -> pd.Series` — z-score rolling

## Gotchas
1. **Contamination parameter.** If unknown, start with 0.01–0.05.
2. **IsolationForest is random.** Set `random_state=42`. Results vary across runs.
3. **LOF is local.** Good for varying-density data. IsolationForest is global.
4. **Don't remove anomalies for financial data** unless clearly erroneous. They carry information.

## References
- Liu et al. (2008). Isolation Forest.
