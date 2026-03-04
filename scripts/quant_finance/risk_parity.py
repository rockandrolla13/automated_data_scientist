"""risk_parity — Equal risk contribution portfolios and HRP."""

from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.optimize import minimize


@dataclass
class RiskParityResult:
    weights: np.ndarray
    risk_contributions: np.ndarray
    portfolio_vol: float
    asset_names: list[str]


def risk_contributions(weights: np.ndarray, Sigma: np.ndarray) -> np.ndarray:
    """Compute marginal risk contribution of each asset."""
    port_vol = np.sqrt(weights @ Sigma @ weights)
    marginal = Sigma @ weights
    rc = weights * marginal / port_vol
    return rc


def risk_parity_weights(
    Sigma: np.ndarray,
    asset_names: list[str] | None = None,
) -> RiskParityResult:
    """Solve for equal risk contribution weights."""
    n = Sigma.shape[0]
    target_rc = 1.0 / n

    def objective(w):
        w = np.abs(w)
        w /= w.sum()
        rc = risk_contributions(w, Sigma)
        port_vol = np.sqrt(w @ Sigma @ w)
        # Minimize squared deviations from target
        return np.sum((rc / port_vol - target_rc) ** 2)

    x0 = np.ones(n) / n
    bounds = [(0.01, None)] * n
    constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}

    res = minimize(objective, x0, method="SLSQP", bounds=bounds, constraints=constraints)
    weights = np.abs(res.x)
    weights /= weights.sum()

    rc = risk_contributions(weights, Sigma)
    port_vol = np.sqrt(weights @ Sigma @ weights)
    names = asset_names or [f"a{i}" for i in range(n)]

    return RiskParityResult(
        weights=weights, risk_contributions=rc,
        portfolio_vol=port_vol, asset_names=names,
    )


def hierarchical_risk_parity(
    returns: pd.DataFrame,
) -> RiskParityResult:
    """Hierarchical Risk Parity (De Prado 2016)."""
    from scipy.cluster.hierarchy import linkage, leaves_list
    from scipy.spatial.distance import squareform

    corr = returns.corr()
    dist = np.sqrt(0.5 * (1 - corr))
    dist_condensed = squareform(dist.values, checks=False)
    link = linkage(dist_condensed, method="single")
    order = leaves_list(link)

    cov = returns.cov().values
    n = cov.shape[0]
    weights = np.ones(n)

    # Recursive bisection
    clusters = [list(order)]
    while len(clusters) > 0:
        new_clusters = []
        for cluster in clusters:
            if len(cluster) <= 1:
                continue
            mid = len(cluster) // 2
            left = cluster[:mid]
            right = cluster[mid:]

            # Inverse-variance allocation between clusters
            def cluster_var(idx):
                c = cov[np.ix_(idx, idx)]
                w = np.ones(len(idx)) / len(idx)
                return w @ c @ w

            v_left = cluster_var(left)
            v_right = cluster_var(right)
            alpha = 1 - v_left / (v_left + v_right) if (v_left + v_right) > 0 else 0.5

            for i in left:
                weights[i] *= alpha
            for i in right:
                weights[i] *= (1 - alpha)

            if len(left) > 1:
                new_clusters.append(left)
            if len(right) > 1:
                new_clusters.append(right)
        clusters = new_clusters

    weights /= weights.sum()
    rc = risk_contributions(weights, cov)
    port_vol = np.sqrt(weights @ cov @ weights)

    return RiskParityResult(
        weights=weights, risk_contributions=rc,
        portfolio_vol=port_vol, asset_names=list(returns.columns),
    )


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    n = 5
    A = rng.normal(size=(n, n))
    Sigma = A.T @ A / 100 + np.eye(n) * 0.01

    result = risk_parity_weights(Sigma, asset_names=[f"Asset_{i}" for i in range(n)])
    print(f"Weights: {result.weights.round(3)}")
    print(f"Risk contributions: {result.risk_contributions.round(4)}")
    print(f"Portfolio vol: {result.portfolio_vol:.4f}")
