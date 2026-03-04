"""portfolio_optimizer — Mean-variance, min-variance, max-Sharpe, efficient frontier via CVXPY."""

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class PortfolioResult:
    weights: np.ndarray
    expected_return: float
    volatility: float
    sharpe: float
    asset_names: list[str]


def mean_variance(
    mu: np.ndarray,
    Sigma: np.ndarray,
    risk_aversion: float = 1.0,
    max_weight: float = 1.0,
    long_only: bool = True,
    asset_names: list[str] | None = None,
) -> PortfolioResult:
    """Mean-variance optimization: max mu'w - (λ/2) w'Σw."""
    import cvxpy as cp

    n = len(mu)
    w = cp.Variable(n)
    ret = mu @ w
    risk = cp.quad_form(w, Sigma)
    objective = cp.Maximize(ret - (risk_aversion / 2) * risk)

    constraints = [cp.sum(w) == 1]
    if long_only:
        constraints.append(w >= 0)
    constraints.append(w <= max_weight)
    if not long_only:
        constraints.append(w >= -max_weight)

    prob = cp.Problem(objective, constraints)
    prob.solve(solver=cp.OSQP)

    weights = np.array(w.value).flatten()
    names = asset_names or [f"a{i}" for i in range(n)]

    return PortfolioResult(
        weights=weights,
        expected_return=float(mu @ weights),
        volatility=float(np.sqrt(weights @ Sigma @ weights)),
        sharpe=float(mu @ weights / np.sqrt(weights @ Sigma @ weights)) if weights @ Sigma @ weights > 0 else 0,
        asset_names=names,
    )


def min_variance(
    Sigma: np.ndarray,
    max_weight: float = 1.0,
    long_only: bool = True,
    asset_names: list[str] | None = None,
) -> PortfolioResult:
    """Global minimum variance portfolio."""
    import cvxpy as cp

    n = Sigma.shape[0]
    w = cp.Variable(n)
    constraints = [cp.sum(w) == 1]
    if long_only:
        constraints.append(w >= 0)
    constraints.append(w <= max_weight)

    prob = cp.Problem(cp.Minimize(cp.quad_form(w, Sigma)), constraints)
    prob.solve(solver=cp.OSQP)

    weights = np.array(w.value).flatten()
    names = asset_names or [f"a{i}" for i in range(n)]

    return PortfolioResult(
        weights=weights, expected_return=0,
        volatility=float(np.sqrt(weights @ Sigma @ weights)),
        sharpe=0, asset_names=names,
    )


def max_sharpe(
    mu: np.ndarray,
    Sigma: np.ndarray,
    rf: float = 0.0,
    max_weight: float = 1.0,
    asset_names: list[str] | None = None,
) -> PortfolioResult:
    """Maximum Sharpe ratio portfolio via transformation."""
    import cvxpy as cp

    n = len(mu)
    excess = mu - rf

    # Transformation: y = w/κ, κ = 1/(excess'w)
    y = cp.Variable(n)
    constraints = [excess @ y == 1, y >= 0]
    prob = cp.Problem(cp.Minimize(cp.quad_form(y, Sigma)), constraints)
    prob.solve(solver=cp.OSQP)

    weights = np.array(y.value).flatten()
    weights = weights / weights.sum()  # normalize
    weights = np.clip(weights, 0, max_weight)
    weights /= weights.sum()

    names = asset_names or [f"a{i}" for i in range(n)]
    vol = float(np.sqrt(weights @ Sigma @ weights))

    return PortfolioResult(
        weights=weights,
        expected_return=float(mu @ weights),
        volatility=vol,
        sharpe=float((mu @ weights - rf) / vol) if vol > 0 else 0,
        asset_names=names,
    )


def efficient_frontier(
    mu: np.ndarray,
    Sigma: np.ndarray,
    n_points: int = 50,
    long_only: bool = True,
) -> pd.DataFrame:
    """Trace the efficient frontier."""
    target_returns = np.linspace(mu.min(), mu.max(), n_points)
    import cvxpy as cp

    n = len(mu)
    rows = []
    for target in target_returns:
        w = cp.Variable(n)
        constraints = [cp.sum(w) == 1, mu @ w >= target]
        if long_only:
            constraints.append(w >= 0)
        prob = cp.Problem(cp.Minimize(cp.quad_form(w, Sigma)), constraints)
        try:
            prob.solve(solver=cp.OSQP)
            if w.value is not None:
                weights = np.array(w.value).flatten()
                vol = np.sqrt(weights @ Sigma @ weights)
                rows.append({"return": float(mu @ weights), "volatility": float(vol)})
        except Exception:
            pass

    return pd.DataFrame(rows)


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    n_assets = 5
    mu = rng.normal(0.08, 0.02, n_assets)
    A = rng.normal(size=(n_assets, n_assets))
    Sigma = A.T @ A / 100 + np.eye(n_assets) * 0.01

    result = mean_variance(mu, Sigma, risk_aversion=2, max_weight=0.4,
                           asset_names=[f"Asset_{i}" for i in range(n_assets)])
    print(f"Weights: {dict(zip(result.asset_names, result.weights.round(3)))}")
    print(f"Return: {result.expected_return:.4f}, Vol: {result.volatility:.4f}, Sharpe: {result.sharpe:.3f}")
