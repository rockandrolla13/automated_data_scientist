"""nelson_siegel — Yield/spread curve fitting via Nelson-Siegel and Svensson."""

from dataclasses import dataclass
import numpy as np
from scipy.optimize import minimize


@dataclass
class NSResult:
    beta0: float  # level
    beta1: float  # slope
    beta2: float  # curvature
    beta3: float | None  # second hump (Svensson only)
    lambda1: float
    lambda2: float | None  # Svensson only
    residuals: np.ndarray
    rmse: float
    model: str


def _ns_curve(tau, beta0, beta1, beta2, lam):
    """Nelson-Siegel yield curve function."""
    x = tau / lam
    exp_x = np.exp(-x)
    factor1 = (1 - exp_x) / x
    factor2 = factor1 - exp_x
    return beta0 + beta1 * factor1 + beta2 * factor2


def _svensson_curve(tau, beta0, beta1, beta2, beta3, lam1, lam2):
    """Svensson extension with second hump."""
    x1 = tau / lam1
    x2 = tau / lam2
    exp1 = np.exp(-x1)
    exp2 = np.exp(-x2)
    f1 = (1 - exp1) / x1
    f2 = f1 - exp1
    f3 = (1 - exp2) / x2 - exp2
    return beta0 + beta1 * f1 + beta2 * f2 + beta3 * f3


def fit_nelson_siegel(
    maturities: np.ndarray,
    yields: np.ndarray,
    lambda_range: tuple = (0.5, 5.0),
    n_grid: int = 20,
) -> NSResult:
    """Fit Nelson-Siegel. Grid search over lambda, then refine."""
    tau = np.asarray(maturities, dtype=float)
    y = np.asarray(yields, dtype=float)

    best_rmse = np.inf
    best_params = None

    for lam in np.linspace(*lambda_range, n_grid):
        x = tau / lam
        exp_x = np.exp(-x)
        X = np.column_stack([
            np.ones_like(tau),
            (1 - exp_x) / x,
            (1 - exp_x) / x - exp_x,
        ])
        betas = np.linalg.lstsq(X, y, rcond=None)[0]
        resid = y - X @ betas
        rmse = np.sqrt(np.mean(resid**2))
        if rmse < best_rmse:
            best_rmse = rmse
            best_params = (*betas, lam)

    b0, b1, b2, lam = best_params
    residuals = y - _ns_curve(tau, b0, b1, b2, lam)

    return NSResult(
        beta0=b0, beta1=b1, beta2=b2, beta3=None,
        lambda1=lam, lambda2=None,
        residuals=residuals, rmse=best_rmse, model="NelsonSiegel",
    )


def fit_svensson(maturities: np.ndarray, yields: np.ndarray) -> NSResult:
    """Fit Svensson model via numerical optimization."""
    tau = np.asarray(maturities, dtype=float)
    y = np.asarray(yields, dtype=float)

    def objective(params):
        b0, b1, b2, b3, l1, l2 = params
        if l1 <= 0.1 or l2 <= 0.1:
            return 1e10
        fitted = _svensson_curve(tau, b0, b1, b2, b3, l1, l2)
        return np.sum((y - fitted)**2)

    # Initial guess from NS
    ns = fit_nelson_siegel(tau, y)
    x0 = [ns.beta0, ns.beta1, ns.beta2, 0.0, ns.lambda1, ns.lambda1 * 2]

    res = minimize(objective, x0, method="Nelder-Mead", options={"maxiter": 10000})
    b0, b1, b2, b3, l1, l2 = res.x
    fitted = _svensson_curve(tau, b0, b1, b2, b3, l1, l2)
    residuals = y - fitted

    return NSResult(
        beta0=b0, beta1=b1, beta2=b2, beta3=b3,
        lambda1=l1, lambda2=l2,
        residuals=residuals, rmse=np.sqrt(np.mean(residuals**2)), model="Svensson",
    )


def evaluate_curve(result: NSResult, maturities: np.ndarray) -> np.ndarray:
    """Evaluate fitted curve at arbitrary maturities."""
    tau = np.asarray(maturities, dtype=float)
    if result.model == "Svensson" and result.beta3 is not None:
        return _svensson_curve(tau, result.beta0, result.beta1, result.beta2,
                                result.beta3, result.lambda1, result.lambda2)
    return _ns_curve(tau, result.beta0, result.beta1, result.beta2, result.lambda1)


if __name__ == "__main__":
    maturities = np.array([0.5, 1, 2, 3, 5, 7, 10, 20, 30])
    yields = np.array([4.8, 4.6, 4.3, 4.1, 4.0, 4.05, 4.15, 4.3, 4.35])
    result = fit_nelson_siegel(maturities, yields)
    print(f"β0={result.beta0:.3f} β1={result.beta1:.3f} β2={result.beta2:.3f} λ={result.lambda1:.3f}")
    print(f"RMSE: {result.rmse:.4f}")
