"""
Variational Inference — fast approximate Bayesian inference.

Usage:
    from scripts.ml_stats.variational_inference import fit_advi, sample_from_vi

    vi_result = fit_advi(model_fn, data, n_iter=30000)
    samples = sample_from_vi(vi_result, n_samples=1000)
"""
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np
import pandas as pd


@dataclass
class VIResult:
    """Variational inference result."""
    approx: object  # PyMC approximation object
    means: dict[str, float]
    stds: dict[str, float]
    elbo_history: np.ndarray
    converged: bool
    method: str  # "advi" or "fullrank_advi"


@dataclass
class VIMCMCComparison:
    """Comparison between VI and MCMC posteriors."""
    kl_divergence: dict[str, float]
    mean_diff: dict[str, float]
    std_ratio: dict[str, float]
    vi_underestimates: bool


def fit_advi(
    model_fn: Callable,
    data: dict,
    n_iter: int = 30000,
    learning_rate: float = 0.01,
    random_seed: int = 42,
) -> VIResult:
    """Fit mean-field ADVI (Automatic Differentiation Variational Inference).

    Args:
        model_fn: Function that takes data dict and returns PyMC model
        data: Data dictionary
        n_iter: Number of optimization iterations
        learning_rate: Adam learning rate
        random_seed: Random seed

    Returns:
        VIResult with approximate posterior
    """
    import pymc as pm

    model = model_fn(data)

    with model:
        approx = pm.fit(
            n=n_iter,
            method="advi",
            random_seed=random_seed,
        )

    # Extract means and stds
    means = {}
    stds = {}

    for var in approx.bij.ordering.vmap:
        var_name = var.name if hasattr(var, "name") else str(var)
        try:
            mean_val = float(approx.mean.eval()[approx.bij.ordering.vmap[var].slc].mean())
            std_val = float(approx.std.eval()[approx.bij.ordering.vmap[var].slc].mean())
            means[var_name] = mean_val
            stds[var_name] = std_val
        except Exception:
            pass

    # Check convergence (ELBO should plateau)
    elbo = -approx.hist
    converged = _check_elbo_convergence(elbo)

    return VIResult(
        approx=approx,
        means=means,
        stds=stds,
        elbo_history=elbo,
        converged=converged,
        method="advi",
    )


def fit_fullrank_advi(
    model_fn: Callable,
    data: dict,
    n_iter: int = 50000,
    learning_rate: float = 0.001,
    random_seed: int = 42,
) -> VIResult:
    """Fit full-rank ADVI (captures posterior correlations).

    Args:
        model_fn: Function that takes data dict and returns PyMC model
        data: Data dictionary
        n_iter: Number of optimization iterations
        learning_rate: Adam learning rate (lower for full-rank)
        random_seed: Random seed

    Returns:
        VIResult with approximate posterior
    """
    import pymc as pm

    model = model_fn(data)

    with model:
        approx = pm.fit(
            n=n_iter,
            method="fullrank_advi",
            random_seed=random_seed,
        )

    # Extract means and stds
    means = {}
    stds = {}

    for var in approx.bij.ordering.vmap:
        var_name = var.name if hasattr(var, "name") else str(var)
        try:
            mean_val = float(approx.mean.eval()[approx.bij.ordering.vmap[var].slc].mean())
            std_val = float(approx.std.eval()[approx.bij.ordering.vmap[var].slc].mean())
            means[var_name] = mean_val
            stds[var_name] = std_val
        except Exception:
            pass

    elbo = -approx.hist
    converged = _check_elbo_convergence(elbo)

    return VIResult(
        approx=approx,
        means=means,
        stds=stds,
        elbo_history=elbo,
        converged=converged,
        method="fullrank_advi",
    )


def _check_elbo_convergence(elbo: np.ndarray, window: int = 1000) -> bool:
    """Check if ELBO has converged (plateau in last iterations)."""
    if len(elbo) < window * 2:
        return False

    # Compare variance in last window vs second-to-last
    last_var = np.var(elbo[-window:])
    prev_var = np.var(elbo[-2*window:-window])

    # Check if variance has stabilized and mean isn't changing much
    mean_change = abs(np.mean(elbo[-window:]) - np.mean(elbo[-2*window:-window]))
    mean_scale = abs(np.mean(elbo[-window:]))

    relative_change = mean_change / (mean_scale + 1e-10)

    return relative_change < 0.01 and last_var < prev_var * 1.5


def sample_from_vi(vi_result: VIResult, n_samples: int = 1000) -> dict[str, np.ndarray]:
    """Draw samples from the variational approximation.

    Args:
        vi_result: Result from fit_advi or fit_fullrank_advi
        n_samples: Number of samples to draw

    Returns:
        Dict mapping variable names to sample arrays
    """
    samples = vi_result.approx.sample(n_samples)

    result = {}
    for var_name in samples.posterior.data_vars:
        # Flatten across chains
        vals = samples.posterior[var_name].values
        result[var_name] = vals.flatten()

    return result


def compare_vi_mcmc(vi_result: VIResult, mcmc_trace) -> VIMCMCComparison:
    """Compare VI approximation to MCMC ground truth.

    Args:
        vi_result: Result from fit_advi or fit_fullrank_advi
        mcmc_trace: ArviZ InferenceData from MCMC sampling

    Returns:
        VIMCMCComparison with divergence metrics
    """
    import arviz as az

    mcmc_summary = az.summary(mcmc_trace)

    kl_divergence = {}
    mean_diff = {}
    std_ratio = {}

    for var_name in vi_result.means:
        if var_name in mcmc_summary.index:
            vi_mean = vi_result.means[var_name]
            vi_std = vi_result.stds[var_name]
            mcmc_mean = float(mcmc_summary.loc[var_name, "mean"])
            mcmc_std = float(mcmc_summary.loc[var_name, "sd"])

            # Approximate KL divergence for Gaussians
            if vi_std > 0 and mcmc_std > 0:
                kl = (
                    np.log(mcmc_std / vi_std)
                    + (vi_std**2 + (vi_mean - mcmc_mean)**2) / (2 * mcmc_std**2)
                    - 0.5
                )
                kl_divergence[var_name] = float(kl)

            mean_diff[var_name] = abs(vi_mean - mcmc_mean)
            std_ratio[var_name] = vi_std / mcmc_std if mcmc_std > 0 else float("inf")

    # VI typically underestimates if std_ratio < 1
    vi_underestimates = np.mean(list(std_ratio.values())) < 0.9

    return VIMCMCComparison(
        kl_divergence=kl_divergence,
        mean_diff=mean_diff,
        std_ratio=std_ratio,
        vi_underestimates=vi_underestimates,
    )


def plot_elbo(vi_result: VIResult) -> None:
    """Plot ELBO convergence curve."""
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 4))
    plt.plot(vi_result.elbo_history)
    plt.xlabel("Iteration")
    plt.ylabel("ELBO")
    plt.title(f"ELBO Convergence ({vi_result.method})")

    # Add smoothed line
    window = min(500, len(vi_result.elbo_history) // 10)
    if window > 1:
        smoothed = np.convolve(
            vi_result.elbo_history,
            np.ones(window) / window,
            mode="valid"
        )
        plt.plot(
            range(window - 1, len(vi_result.elbo_history)),
            smoothed,
            "r-",
            linewidth=2,
            label="Smoothed",
        )
        plt.legend()

    plt.tight_layout()


if __name__ == "__main__":
    import pymc as pm

    # Example: normal model
    np.random.seed(42)
    true_mu, true_sigma = 2.5, 1.2
    y_obs = np.random.normal(true_mu, true_sigma, size=100)

    def normal_model(data):
        with pm.Model() as model:
            mu = pm.Normal("mu", mu=0, sigma=5)
            sigma = pm.HalfNormal("sigma", sigma=2)
            y = pm.Normal("y", mu=mu, sigma=sigma, observed=data["y"])
        return model

    result = fit_advi(normal_model, {"y": y_obs}, n_iter=10000)

    print("=== VI Results ===")
    print(f"Converged: {result.converged}")
    print(f"Approximate mean mu: {result.means.get('mu', 'N/A')}")
    print(f"Approximate std mu: {result.stds.get('mu', 'N/A')}")
