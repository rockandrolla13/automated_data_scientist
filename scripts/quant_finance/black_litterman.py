"""black_litterman — Black-Litterman model: combine market equilibrium with subjective views."""

from dataclasses import dataclass
import numpy as np


@dataclass
class BLResult:
    combined_returns: np.ndarray
    combined_covariance: np.ndarray
    equilibrium_returns: np.ndarray
    weights: np.ndarray
    asset_names: list[str]


def equilibrium_returns(
    Sigma: np.ndarray,
    market_weights: np.ndarray,
    delta: float = 2.5,
) -> np.ndarray:
    """Implied equilibrium excess returns: Π = δΣw_mkt."""
    return delta * Sigma @ market_weights


def black_litterman(
    Sigma: np.ndarray,
    market_weights: np.ndarray,
    P: np.ndarray,
    Q: np.ndarray,
    omega: np.ndarray | None = None,
    tau: float = 0.05,
    delta: float = 2.5,
    asset_names: list[str] | None = None,
) -> BLResult:
    """Black-Litterman combined return and covariance.

    Args:
        Sigma: Covariance matrix (n × n)
        market_weights: Market cap weights (n,)
        P: Pick matrix (k × n) — k views on n assets
        Q: View returns (k,) — expected returns from views
        omega: View uncertainty (k × k). Default: proportional to P Σ P'
        tau: Scalar uncertainty on equilibrium (0.01–0.05)
        delta: Risk aversion coefficient
    """
    n = Sigma.shape[0]
    Pi = equilibrium_returns(Sigma, market_weights, delta)

    tau_Sigma = tau * Sigma

    if omega is None:
        # Proportional to view portfolio variance
        omega = np.diag(np.diag(P @ tau_Sigma @ P.T))

    # BL formula
    tau_Sigma_inv = np.linalg.inv(tau_Sigma)
    omega_inv = np.linalg.inv(omega)

    M = np.linalg.inv(tau_Sigma_inv + P.T @ omega_inv @ P)
    mu_BL = M @ (tau_Sigma_inv @ Pi + P.T @ omega_inv @ Q)

    # Combined covariance
    Sigma_BL = Sigma + M

    # Optimal weights from combined returns
    weights = np.linalg.inv(delta * Sigma_BL) @ mu_BL
    weights = weights / np.sum(np.abs(weights))  # normalize

    names = asset_names or [f"a{i}" for i in range(n)]

    return BLResult(
        combined_returns=mu_BL,
        combined_covariance=Sigma_BL,
        equilibrium_returns=Pi,
        weights=weights,
        asset_names=names,
    )


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    n = 4
    names = ["IG", "HY", "EM", "Govies"]

    A = rng.normal(size=(n, n))
    Sigma = A.T @ A / 500 + np.eye(n) * 0.005
    mkt_w = np.array([0.3, 0.2, 0.15, 0.35])

    # View: IG outperforms HY by 1%
    P = np.array([[1, -1, 0, 0]])
    Q = np.array([0.01])

    result = black_litterman(Sigma, mkt_w, P, Q, asset_names=names)
    print("Equilibrium returns:", dict(zip(names, result.equilibrium_returns.round(4))))
    print("BL returns:", dict(zip(names, result.combined_returns.round(4))))
    print("BL weights:", dict(zip(names, result.weights.round(3))))
