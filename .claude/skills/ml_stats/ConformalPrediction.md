# ConformalPrediction

## When to Use
- Distribution-free prediction intervals with coverage guarantees.
- Any point forecast model → calibrated prediction interval.
- When you need honest uncertainty quantification without distributional assumptions.

## Packages
```python
from mapie.regression import MapieRegressor
from mapie.classification import MapieClassifier
```

## Mathematical Background
Split conformal: fit model on train, compute residuals on calibration set, use quantile of |residuals| as band width. Guarantees P(Y ∈ Ĉ) ≥ 1-α marginally.

## Corresponding Script
`/scripts/ml_stats/conformal_prediction.py`
- `conformal_regression(model, X_cal, y_cal, X_test, alpha) -> ConformalResult`
- `conformal_classification(model, X_cal, y_cal, X_test, alpha) -> ConformalResult`
- `check_coverage(y_true, lower, upper) -> float` — empirical coverage

## Gotchas
1. **Marginal, not conditional.** Coverage is average over X, not for each X. Can be loose locally.
2. **Calibration set must be separate** from train. Use validation split.
3. **Exchangeability assumption.** Time series violates this. Use ACI (Adaptive Conformal Inference) for sequential.
4. **Wider ≠ worse.** Honest uncertainty > narrow but miscalibrated intervals.

## Interpretation Guide
| Metric | Target | Problem if |
|--------|--------|-----------|
| Empirical coverage | ≥ 1-α | < 1-α → leakage or non-exchangeability |
| Mean interval width | Smaller = better | Very wide → model is uncertain, improve point forecast |

## References
- Vovk et al. (2005). Algorithmic Learning in a Random World.
- MAPIE: https://mapie.readthedocs.io/
- Gibbs & Candès (2021). Adaptive Conformal Inference Under Distribution Shift.
