"""gaussian_process — GP regression with uncertainty and Bayesian optimization."""

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class GPResult:
    model: object
    marginal_likelihood: float
    kernel_params: dict
    X_train: np.ndarray
    y_train: np.ndarray


def fit_gp(
    X: np.ndarray,
    y: np.ndarray,
    kernel: str = "matern",
    normalize_y: bool = True,
    random_state: int = 42,
) -> GPResult:
    """Fit Gaussian Process regression."""
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import (
        RBF, Matern, WhiteKernel, ConstantKernel as C,
    )

    kernels = {
        "rbf": C(1.0) * RBF(length_scale=1.0) + WhiteKernel(noise_level=0.1),
        "matern": C(1.0) * Matern(length_scale=1.0, nu=1.5) + WhiteKernel(noise_level=0.1),
        "matern25": C(1.0) * Matern(length_scale=1.0, nu=2.5) + WhiteKernel(noise_level=0.1),
    }
    k = kernels.get(kernel, kernels["matern"])

    gpr = GaussianProcessRegressor(kernel=k, normalize_y=normalize_y,
                                    random_state=random_state, n_restarts_optimizer=5)
    gpr.fit(X, y)

    return GPResult(
        model=gpr, marginal_likelihood=gpr.log_marginal_likelihood_value_,
        kernel_params=dict(zip(gpr.kernel_.get_params().keys(), gpr.kernel_.get_params().values())),
        X_train=X, y_train=y,
    )


def predict_with_uncertainty(
    result: GPResult,
    X_new: np.ndarray,
) -> pd.DataFrame:
    """Predict mean ± std."""
    mean, std = result.model.predict(X_new, return_std=True)
    return pd.DataFrame({
        "mean": mean, "std": std,
        "lower_95": mean - 1.96 * std,
        "upper_95": mean + 1.96 * std,
    })


def optimize_acquisition(
    result: GPResult,
    bounds: np.ndarray,
    n_candidates: int = 1000,
    acq_fn: str = "ei",
    xi: float = 0.01,
) -> np.ndarray:
    """Simple Bayesian optimization step: find next point to evaluate."""
    from scipy.stats import norm

    X_cand = np.random.uniform(bounds[:, 0], bounds[:, 1], size=(n_candidates, bounds.shape[0]))
    mean, std = result.model.predict(X_cand, return_std=True)
    y_best = result.y_train.max()

    if acq_fn == "ei":
        z = (mean - y_best - xi) / (std + 1e-10)
        ei = (mean - y_best - xi) * norm.cdf(z) + std * norm.pdf(z)
        ei[std < 1e-10] = 0
        return X_cand[np.argmax(ei)]
    elif acq_fn == "ucb":
        ucb = mean + 2.0 * std
        return X_cand[np.argmax(ucb)]
    else:
        raise ValueError(f"Unknown acq_fn: {acq_fn}")


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    X = rng.uniform(0, 5, (50, 1))
    y = np.sin(X.ravel()) + rng.normal(scale=0.1, size=50)

    result = fit_gp(X, y, kernel="matern")
    X_new = np.linspace(0, 5, 100).reshape(-1, 1)
    preds = predict_with_uncertainty(result, X_new)
    print(f"Log-marginal-likelihood: {result.marginal_likelihood:.2f}")
    print(preds.head())
