"""conformal_prediction — Distribution-free prediction intervals via MAPIE."""

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class ConformalResult:
    point_predictions: np.ndarray
    lower: np.ndarray
    upper: np.ndarray
    alpha: float
    empirical_coverage: float | None
    mean_width: float


def conformal_regression(
    model,
    X_cal: np.ndarray,
    y_cal: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray | None = None,
    alpha: float = 0.10,
    method: str = "plus",
) -> ConformalResult:
    """Wrap any sklearn regressor with conformal prediction intervals."""
    from mapie.regression import MapieRegressor

    mapie = MapieRegressor(estimator=model, method=method, cv="prefit")
    mapie.fit(X_cal, y_cal)
    preds, intervals = mapie.predict(X_test, alpha=alpha)

    lower = intervals[:, 0, 0]
    upper = intervals[:, 1, 0]

    coverage = None
    if y_test is not None:
        coverage = np.mean((y_test >= lower) & (y_test <= upper))

    return ConformalResult(
        point_predictions=preds, lower=lower, upper=upper,
        alpha=alpha, empirical_coverage=coverage,
        mean_width=np.mean(upper - lower),
    )


def split_conformal_manual(
    residuals_cal: np.ndarray,
    predictions_test: np.ndarray,
    alpha: float = 0.10,
    y_test: np.ndarray | None = None,
) -> ConformalResult:
    """Manual split conformal — when MAPIE doesn't fit the use case."""
    abs_res = np.abs(residuals_cal)
    n = len(abs_res)
    q = np.quantile(abs_res, np.ceil((1 - alpha) * (n + 1)) / n)

    lower = predictions_test - q
    upper = predictions_test + q

    coverage = None
    if y_test is not None:
        coverage = np.mean((y_test >= lower) & (y_test <= upper))

    return ConformalResult(
        point_predictions=predictions_test, lower=lower, upper=upper,
        alpha=alpha, empirical_coverage=coverage,
        mean_width=2 * q,
    )


def check_coverage(y_true: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> float:
    """Compute empirical coverage."""
    return float(np.mean((y_true >= lower) & (y_true <= upper)))


if __name__ == "__main__":
    from sklearn.ensemble import GradientBoostingRegressor
    rng = np.random.default_rng(42)
    X = rng.normal(size=(500, 5))
    y = X @ rng.normal(size=5) + rng.normal(scale=0.5, size=500)

    model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    model.fit(X[:300], y[:300])

    result = conformal_regression(model, X[300:400], y[300:400], X[400:], y[400:], alpha=0.10)
    print(f"Coverage: {result.empirical_coverage:.3f} (target: 0.90)")
    print(f"Mean width: {result.mean_width:.3f}")
