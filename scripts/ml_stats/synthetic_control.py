"""synthetic_control — Synthetic control method with placebo tests."""

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class SyntheticControlResult:
    weights: np.ndarray
    donor_names: list[str]
    synthetic: pd.Series
    treated: pd.Series
    gap: pd.Series  # treated - synthetic
    pre_rmse: float
    post_effect: float


def fit_synthetic_control(
    treated: pd.Series,
    donors: pd.DataFrame,
    pre_end: str | int,
) -> SyntheticControlResult:
    """Fit synthetic control via constrained least squares."""
    import cvxpy as cp

    if isinstance(pre_end, str):
        pre_mask = treated.index <= pre_end
    else:
        pre_mask = np.arange(len(treated)) < pre_end

    y_pre = treated[pre_mask].values
    X_pre = donors[pre_mask].values

    n_donors = X_pre.shape[1]
    w = cp.Variable(n_donors)
    objective = cp.Minimize(cp.sum_squares(X_pre @ w - y_pre))
    constraints = [w >= 0, cp.sum(w) == 1]
    prob = cp.Problem(objective, constraints)
    prob.solve(solver=cp.OSQP)

    weights = np.array(w.value).flatten()
    weights = np.maximum(weights, 0)
    weights /= weights.sum()

    synthetic = pd.Series(donors.values @ weights, index=treated.index, name="synthetic")
    gap = treated - synthetic

    pre_rmse = np.sqrt(np.mean((treated[pre_mask] - synthetic[pre_mask]) ** 2))
    post_effect = gap[~pre_mask].mean()

    return SyntheticControlResult(
        weights=weights, donor_names=list(donors.columns),
        synthetic=synthetic, treated=treated, gap=gap,
        pre_rmse=pre_rmse, post_effect=post_effect,
    )


def placebo_test(
    donors: pd.DataFrame,
    pre_end: str | int,
) -> pd.DataFrame:
    """Leave-one-out placebo: treat each donor as fake treated."""
    results = []
    for col in donors.columns:
        fake_treated = donors[col]
        remaining = donors.drop(columns=[col])
        try:
            res = fit_synthetic_control(fake_treated, remaining, pre_end)
            results.append({"unit": col, "post_effect": res.post_effect, "pre_rmse": res.pre_rmse})
        except Exception:
            results.append({"unit": col, "post_effect": np.nan, "pre_rmse": np.nan})
    return pd.DataFrame(results)


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    idx = pd.date_range("2020-01-01", periods=200, freq="B")
    donors = pd.DataFrame(rng.normal(size=(200, 5)), index=idx, columns=[f"d{i}" for i in range(5)])
    treated = donors @ rng.dirichlet(np.ones(5)) + rng.normal(scale=0.1, size=200)
    treated = pd.Series(treated, index=idx, name="treated")
    treated.iloc[150:] += 0.5  # treatment effect

    result = fit_synthetic_control(treated, donors, pre_end=idx[149])
    print(f"Post-treatment effect: {result.post_effect:.3f}")
    print(f"Pre-treatment RMSE: {result.pre_rmse:.4f}")
    print(f"Weights: {dict(zip(result.donor_names, result.weights.round(3)))}")
