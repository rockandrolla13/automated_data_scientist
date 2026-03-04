"""bayesian_regression — Bayesian linear regression via PyMC."""

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class BayesianResult:
    trace: object  # arviz InferenceData
    summary: pd.DataFrame
    coefficients_mean: dict[str, float]
    coefficients_hdi: dict[str, tuple]
    sigma: float
    rhat_ok: bool
    divergences: int


def fit_bayesian_linear(
    X: np.ndarray | pd.DataFrame,
    y: np.ndarray | pd.Series,
    feature_names: list[str] | None = None,
    prior_std: float = 10.0,
    draws: int = 2000,
    tune: int = 1000,
    target_accept: float = 0.9,
    random_seed: int = 42,
) -> BayesianResult:
    """Fit Bayesian linear regression with Normal priors."""
    import pymc as pm
    import arviz as az

    X = np.asarray(X)
    y = np.asarray(y).ravel()
    n_features = X.shape[1]
    names = feature_names or [f"beta_{i}" for i in range(n_features)]

    with pm.Model() as model:
        beta = pm.Normal("beta", mu=0, sigma=prior_std, shape=n_features)
        sigma = pm.HalfNormal("sigma", sigma=1)
        mu = pm.math.dot(X, beta)
        likelihood = pm.Normal("y", mu=mu, sigma=sigma, observed=y)

        trace = pm.sample(draws=draws, tune=tune, target_accept=target_accept,
                          random_seed=random_seed, progressbar=False)

    summary = az.summary(trace, var_names=["beta", "sigma"])
    divergences = trace.sample_stats.diverging.sum().item()

    coef_mean = {}
    coef_hdi = {}
    for i, name in enumerate(names):
        vals = trace.posterior["beta"].values[:, :, i].flatten()
        coef_mean[name] = float(np.mean(vals))
        hdi = az.hdi(vals, hdi_prob=0.94)
        coef_hdi[name] = (float(hdi[0]), float(hdi[1]))

    rhat_ok = all(summary["r_hat"] < 1.05)

    return BayesianResult(
        trace=trace, summary=summary,
        coefficients_mean=coef_mean, coefficients_hdi=coef_hdi,
        sigma=float(trace.posterior["sigma"].mean()),
        rhat_ok=rhat_ok, divergences=divergences,
    )


def posterior_predictive(
    result: BayesianResult,
    X_new: np.ndarray,
) -> pd.DataFrame:
    """Generate posterior predictive samples."""
    betas = result.trace.posterior["beta"].values
    sigma_vals = result.trace.posterior["sigma"].values
    n_chains, n_draws, n_features = betas.shape

    betas_flat = betas.reshape(-1, n_features)
    sigma_flat = sigma_vals.flatten()

    mu = X_new @ betas_flat.T
    preds = mu + np.random.normal(0, sigma_flat, size=mu.shape)

    return pd.DataFrame({
        "mean": mu.mean(axis=1),
        "std": mu.std(axis=1),
        "lower_3": np.percentile(preds, 3, axis=1),
        "upper_97": np.percentile(preds, 97, axis=1),
    })


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    X = rng.normal(size=(200, 3))
    y = X @ np.array([1.5, -0.5, 0.8]) + rng.normal(scale=0.3, size=200)

    result = fit_bayesian_linear(X, y, feature_names=["x1", "x2", "x3"])
    print(f"Coefficients: {result.coefficients_mean}")
    print(f"Divergences: {result.divergences}, Rhat OK: {result.rhat_ok}")
