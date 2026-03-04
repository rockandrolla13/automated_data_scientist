---
name: bayesian-regression
description: Use when performing regression with uncertainty on parameters or incorporating prior knowledge into estimation.
---

# BayesianRegression

## When to Use
- Regression with uncertainty on parameters (not just predictions).
- Incorporating prior knowledge (e.g., factor loadings should be positive).
- Small sample sizes where frequentist estimates are unstable.

## Packages
```python
import pymc as pm
import arviz as az
```

## Mathematical Background
$y \sim N(X\beta, \sigma^2)$ with priors $\beta \sim N(\mu_0, \Sigma_0)$, $\sigma \sim \text{HalfNormal}(\tau)$.
Posterior via MCMC (NUTS sampler). Inference is on the full posterior distribution.

## Corresponding Script
`/scripts/ml_stats/bayesian_regression.py`
- `fit_bayesian_linear(X, y, priors) -> BayesianResult`
- `posterior_predictive(result, X_new) -> pd.DataFrame`
- `diagnostics(result) -> dict` — Rhat, ESS, divergences

## Gotchas
1. **NUTS needs >1000 samples.** Default 2000 draws + 1000 tune is fine.
2. **Divergences = bad.** If >0 divergences, increase `target_accept` to 0.95+.
3. **Prior sensitivity.** Always run with 2+ prior specifications to check robustness.
4. **Slow on large n.** For n > 10k, consider variational inference (`pm.fit()`).

## Interpretation Guide
| Diagnostic | Good | Bad |
|-----------|------|-----|
| Rhat | < 1.01 | > 1.05 → chains haven't converged |
| ESS | > 400 per parameter | < 100 → increase samples |
| Divergences | 0 | > 0 → model misspecified or step size issue |

## References
- Gelman et al. (2013). Bayesian Data Analysis.
- PyMC: https://www.pymc.io/
