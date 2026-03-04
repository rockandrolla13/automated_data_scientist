"""merton_model — Structural credit risk: distance-to-default, PD, implied asset vol."""

from dataclasses import dataclass
import numpy as np
from scipy.optimize import fsolve
from scipy.stats import norm


@dataclass
class MertonResult:
    asset_value: float
    asset_vol: float
    distance_to_default: float
    default_probability: float
    equity_value_check: float
    converged: bool


def _merton_equations(params, equity, equity_vol, debt, r, T):
    """System of 2 equations for Merton model."""
    V, sigma_V = params
    d1 = (np.log(V / debt) + (r + 0.5 * sigma_V**2) * T) / (sigma_V * np.sqrt(T))
    d2 = d1 - sigma_V * np.sqrt(T)

    # Equation 1: Equity value
    eq1 = V * norm.cdf(d1) - debt * np.exp(-r * T) * norm.cdf(d2) - equity
    # Equation 2: Equity vol relationship
    eq2 = norm.cdf(d1) * sigma_V * V / equity - equity_vol

    return [eq1, eq2]


def solve_merton(
    equity: float,
    equity_vol: float,
    debt: float,
    r: float = 0.05,
    T: float = 1.0,
    mu: float | None = None,
) -> MertonResult:
    """Solve Merton model for asset value and asset volatility.

    Args:
        equity: Market cap (same units as debt)
        equity_vol: Annualized equity volatility (decimal)
        debt: Face value of debt (short-term + 0.5 × long-term)
        r: Risk-free rate (decimal)
        T: Time horizon (years)
        mu: Real-world drift for DD calculation (default = r)
    """
    mu = mu if mu is not None else r

    # Initial guess: V = E + D, sigma_V = sigma_E * E / V
    V0 = equity + debt
    sigma_V0 = equity_vol * equity / V0

    solution, info, ier, msg = fsolve(
        _merton_equations, [V0, sigma_V0],
        args=(equity, equity_vol, debt, r, T),
        full_output=True,
    )

    V, sigma_V = solution
    sigma_V = abs(sigma_V)
    converged = ier == 1

    # Distance to default (real-world measure)
    dd = (np.log(V / debt) + (mu - 0.5 * sigma_V**2) * T) / (sigma_V * np.sqrt(T))
    pd_val = norm.cdf(-dd)

    # Verify equity value
    d1 = (np.log(V / debt) + (r + 0.5 * sigma_V**2) * T) / (sigma_V * np.sqrt(T))
    d2 = d1 - sigma_V * np.sqrt(T)
    equity_check = V * norm.cdf(d1) - debt * np.exp(-r * T) * norm.cdf(d2)

    return MertonResult(
        asset_value=V, asset_vol=sigma_V,
        distance_to_default=dd, default_probability=pd_val,
        equity_value_check=equity_check, converged=converged,
    )


def distance_to_default(V: float, debt: float, mu: float, sigma_V: float, T: float) -> float:
    """Standalone DD calculation."""
    return (np.log(V / debt) + (mu - 0.5 * sigma_V**2) * T) / (sigma_V * np.sqrt(T))


def implied_spread(pd_val: float, lgd: float = 0.6, T: float = 5.0) -> float:
    """Approximate fair CDS spread from PD and LGD. Returns bps."""
    # s ≈ PD × LGD / risky_duration ≈ PD × LGD × (1/T) annualized
    # More precisely: s ≈ -ln(1 - PD) × LGD / T × 10000
    hazard = -np.log(1 - pd_val) / T if pd_val < 1 else 100
    return hazard * lgd * 10000


if __name__ == "__main__":
    import json
    result = solve_merton(equity=500, equity_vol=0.30, debt=800, r=0.05, T=1.0)
    print(f"Asset value: {result.asset_value:.1f}")
    print(f"Asset vol: {result.asset_vol:.4f}")
    print(f"DD: {result.distance_to_default:.2f}")
    print(f"PD: {result.default_probability:.4%}")
    print(f"Implied spread: {implied_spread(result.default_probability):.0f} bps")

    with open("results.json", "w") as f:
        json.dump({
            "asset_value": round(result.asset_value, 2),
            "asset_vol": round(result.asset_vol, 4),
            "distance_to_default": round(result.distance_to_default, 4),
            "default_probability": round(result.default_probability, 6),
            "converged": result.converged,
        }, f, indent=2)
