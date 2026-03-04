"""shap_explainer — SHAP-based model interpretation."""

from dataclasses import dataclass
import numpy as np
import pandas as pd
from pathlib import Path


@dataclass
class SHAPResult:
    shap_values: np.ndarray
    base_value: float
    feature_names: list[str]
    feature_importance: pd.Series  # mean |SHAP| per feature


def explain_model(
    model,
    X: np.ndarray | pd.DataFrame,
    feature_names: list[str] | None = None,
    explainer_type: str = "auto",
    max_samples: int = 500,
) -> SHAPResult:
    """Compute SHAP values. Auto-selects TreeExplainer or KernelExplainer."""
    import shap

    if isinstance(X, pd.DataFrame):
        feature_names = feature_names or list(X.columns)
        X_arr = X.values
    else:
        X_arr = X
        feature_names = feature_names or [f"f{i}" for i in range(X_arr.shape[1])]

    if explainer_type == "auto":
        try:
            explainer = shap.TreeExplainer(model)
        except Exception:
            background = shap.kmeans(X_arr[:min(100, len(X_arr))], 50)
            explainer = shap.KernelExplainer(model.predict, background)
    elif explainer_type == "tree":
        explainer = shap.TreeExplainer(model)
    else:
        background = shap.kmeans(X_arr[:min(100, len(X_arr))], 50)
        explainer = shap.KernelExplainer(model.predict, background)

    X_sample = X_arr[:max_samples]
    sv = explainer.shap_values(X_sample)

    if isinstance(sv, list):
        sv = sv[1]  # binary classification: class 1

    base = explainer.expected_value
    if isinstance(base, (list, np.ndarray)):
        base = base[1] if len(base) > 1 else base[0]

    importance = pd.Series(np.abs(sv).mean(axis=0), index=feature_names).sort_values(ascending=False)

    return SHAPResult(shap_values=sv, base_value=float(base),
                      feature_names=feature_names, feature_importance=importance)


def plot_summary(result: SHAPResult, X: np.ndarray | pd.DataFrame, path: str | None = None) -> None:
    """SHAP beeswarm summary plot."""
    import shap
    import matplotlib.pyplot as plt

    shap.summary_plot(result.shap_values, X, feature_names=result.feature_names, show=False)
    if path:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()


if __name__ == "__main__":
    from sklearn.ensemble import GradientBoostingRegressor
    rng = np.random.default_rng(42)
    X = rng.normal(size=(300, 5))
    y = X @ np.array([2, -1, 0.5, 0, 0]) + rng.normal(scale=0.5, size=300)

    model = GradientBoostingRegressor(n_estimators=100, random_state=42).fit(X, y)
    result = explain_model(model, X, feature_names=[f"x{i}" for i in range(5)])
    print("Feature importance (mean |SHAP|):")
    print(result.feature_importance)
