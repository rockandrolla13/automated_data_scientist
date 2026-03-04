"""
MCMC — Markov Chain Monte Carlo for full Bayesian inference.

Usage:
    from scripts.ml_stats.mcmc import sample_posterior, diagnose_chains

    def model_fn(data):
        import pymc as pm
        with pm.Model() as model:
            mu = pm.Normal("mu", 0, 1)
            sigma = pm.HalfNormal("sigma", 1)
            y = pm.Normal("y", mu, sigma, observed=data["y"])
        return model

    trace = sample_posterior(model_fn, data)
    diagnostics = diagnose_chains(trace)
"""
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np
import pandas as pd


@dataclass
class DiagnosticsResult:
    """MCMC chain diagnostics."""
    r_hat: dict[str, float]
    ess: dict[str, float]
    divergences: int
    converged: bool
    warnings: list[str]


@dataclass
class MCMCResult:
    """MCMC sampling result."""
    trace: object  # arviz InferenceData
    diagnostics: DiagnosticsResult
    posterior_means: dict[str, float]
    hdi_94: dict[str, tuple[float, float]]


@dataclass
class ComparisonResult:
    """Model comparison result."""
    comparison_df: pd.DataFrame
    best_model: str
    weights: dict[str, float]


def sample_posterior(
    model_fn: Callable,
    data: dict,
    n_samples: int = 2000,
    n_chains: int = 4,
    n_warmup: int = 1000,
    random_seed: int = 42,
    target_accept: float = 0.9,
) -> MCMCResult:
    """Run MCMC sampling on a PyMC model.

    Args:
        model_fn: Function that takes data dict and returns a PyMC model
        data: Data dictionary passed to model_fn
        n_samples: Number of samples per chain (post-warmup)
        n_chains: Number of parallel chains
        n_warmup: Number of warmup/tuning samples
        random_seed: Random seed for reproducibility
        target_accept: Target acceptance rate (increase if divergences)

    Returns:
        MCMCResult with trace, diagnostics, posterior summaries
    """
    import pymc as pm
    import arviz as az

    model = model_fn(data)

    with model:
        trace = pm.sample(
            draws=n_samples,
            tune=n_warmup,
            chains=n_chains,
            random_seed=random_seed,
            target_accept=target_accept,
            return_inferencedata=True,
        )

    diagnostics = diagnose_chains(trace)

    # Extract posterior summaries
    summary = az.summary(trace, hdi_prob=0.94)
    posterior_means = {}
    hdi_94 = {}

    for var in summary.index:
        posterior_means[var] = float(summary.loc[var, "mean"])
        hdi_94[var] = (
            float(summary.loc[var, "hdi_3%"]),
            float(summary.loc[var, "hdi_97%"]),
        )

    return MCMCResult(
        trace=trace,
        diagnostics=diagnostics,
        posterior_means=posterior_means,
        hdi_94=hdi_94,
    )


def diagnose_chains(trace) -> DiagnosticsResult:
    """Check MCMC chain convergence and quality.

    Args:
        trace: ArviZ InferenceData object

    Returns:
        DiagnosticsResult with r_hat, ESS, divergences, convergence status
    """
    import arviz as az

    summary = az.summary(trace)

    r_hat = {}
    ess = {}
    warnings = []

    for var in summary.index:
        r_hat[var] = float(summary.loc[var, "r_hat"])
        ess[var] = float(summary.loc[var, "ess_bulk"])

        if r_hat[var] > 1.01:
            warnings.append(f"{var}: r_hat={r_hat[var]:.3f} > 1.01 (not converged)")
        if ess[var] < 400:
            warnings.append(f"{var}: ESS={ess[var]:.0f} < 400 (low effective samples)")

    # Count divergences
    divergences = 0
    if hasattr(trace, "sample_stats") and "diverging" in trace.sample_stats:
        divergences = int(trace.sample_stats["diverging"].sum())
        if divergences > 0:
            warnings.append(f"{divergences} divergences detected (geometry issues)")

    converged = (
        all(r < 1.01 for r in r_hat.values())
        and all(e >= 400 for e in ess.values())
        and divergences == 0
    )

    return DiagnosticsResult(
        r_hat=r_hat,
        ess=ess,
        divergences=divergences,
        converged=converged,
        warnings=warnings,
    )


def posterior_predictive(
    trace,
    model_fn: Callable,
    data: dict,
    n_samples: Optional[int] = None,
) -> np.ndarray:
    """Generate posterior predictive samples.

    Args:
        trace: ArviZ InferenceData from sample_posterior
        model_fn: Same model function used for sampling
        data: Data dict (can include new X values)
        n_samples: Number of samples (None = use all posterior samples)

    Returns:
        Array of shape (n_samples, n_observations)
    """
    import pymc as pm

    model = model_fn(data)

    with model:
        ppc = pm.sample_posterior_predictive(
            trace,
            var_names=["y"],  # Assumes observed variable is named "y"
            random_seed=42,
        )

    # Extract predictions
    y_pred = ppc.posterior_predictive["y"].values

    # Reshape from (chain, draw, obs) to (samples, obs)
    n_chains, n_draws = y_pred.shape[:2]
    y_pred = y_pred.reshape(n_chains * n_draws, -1)

    if n_samples is not None:
        idx = np.random.choice(len(y_pred), size=n_samples, replace=False)
        y_pred = y_pred[idx]

    return y_pred


def compare_models(
    traces: list,
    model_names: list[str],
) -> ComparisonResult:
    """Compare models using WAIC and LOO-CV.

    Args:
        traces: List of ArviZ InferenceData objects
        model_names: Names for each model

    Returns:
        ComparisonResult with comparison DataFrame and best model
    """
    import arviz as az

    # Build comparison dict
    model_dict = {name: trace for name, trace in zip(model_names, traces)}

    # Compare using LOO (leave-one-out cross-validation)
    comparison = az.compare(model_dict, ic="loo")

    # Extract weights
    weights = {name: float(comparison.loc[name, "weight"]) for name in model_names}

    # Best model is first row
    best_model = comparison.index[0]

    return ComparisonResult(
        comparison_df=comparison,
        best_model=best_model,
        weights=weights,
    )


def plot_diagnostics(trace, var_names: Optional[list[str]] = None) -> None:
    """Plot trace and posterior diagnostics.

    Args:
        trace: ArviZ InferenceData
        var_names: Variables to plot (None = all)
    """
    import arviz as az
    import matplotlib.pyplot as plt

    # Trace plot
    az.plot_trace(trace, var_names=var_names)
    plt.tight_layout()

    # Posterior plot
    az.plot_posterior(trace, var_names=var_names, hdi_prob=0.94)
    plt.tight_layout()


if __name__ == "__main__":
    # Example: simple normal model
    import pymc as pm

    # Generate fake data
    np.random.seed(42)
    true_mu, true_sigma = 2.5, 1.2
    y_obs = np.random.normal(true_mu, true_sigma, size=100)

    def normal_model(data):
        with pm.Model() as model:
            mu = pm.Normal("mu", mu=0, sigma=5)
            sigma = pm.HalfNormal("sigma", sigma=2)
            y = pm.Normal("y", mu=mu, sigma=sigma, observed=data["y"])
        return model

    result = sample_posterior(normal_model, {"y": y_obs}, n_samples=1000, n_chains=2)

    print("=== MCMC Results ===")
    print(f"Converged: {result.diagnostics.converged}")
    print(f"Posterior mean mu: {result.posterior_means['mu']:.3f} (true: {true_mu})")
    print(f"Posterior mean sigma: {result.posterior_means['sigma']:.3f} (true: {true_sigma})")
    print(f"94% HDI mu: {result.hdi_94['mu']}")

    if result.diagnostics.warnings:
        print("\nWarnings:")
        for w in result.diagnostics.warnings:
            print(f"  - {w}")
