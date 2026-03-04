---
name: mcmc
description: Markov Chain Monte Carlo for full Bayesian posterior estimation. Use when you need credible intervals, posterior predictive checks, or model comparison via WAIC/LOO.
---

# MCMC — Full Bayesian Inference

## When to Use
- Need full posterior distribution, not just point estimates
- Credible intervals on parameters (e.g., default probability, recovery rate)
- Posterior predictive checks to validate model assumptions
- Comparing multiple models via information criteria (WAIC, LOO-CV)
- Hierarchical models (e.g., sector-level priors on issuer defaults)

## Packages
- `pymc>=5.10` — primary MCMC framework
- `arviz>=0.17` — diagnostics and visualization
- `numpyro>=0.14` — fast JAX-native alternative for speed

## Functions (scripts/ml_stats/mcmc.py)

### `sample_posterior(model_fn, data, n_samples=2000, n_chains=4, n_warmup=1000)`
Run MCMC sampling. Returns trace object with posterior samples.

### `diagnose_chains(trace)`
Check convergence: r_hat < 1.01, ESS > 400, no divergences. Returns DiagnosticsResult.

### `posterior_predictive(trace, model_fn, X_new)`
Generate predictions from the posterior. Returns samples × observations array.

### `compare_models(traces, model_names)`
Compare models via WAIC and LOO-CV. Returns comparison DataFrame.

## Math Background
MCMC constructs a Markov chain whose stationary distribution is the posterior:
$$p(\theta | D) \propto p(D | \theta) \cdot p(\theta)$$

NUTS (No-U-Turn Sampler) adaptively sets step size and trajectory length to efficiently explore the posterior.

## Finance Use Cases
1. **Merton model posterior** — estimate asset volatility and drift with uncertainty
2. **Hierarchical default models** — sector-level priors, issuer-level params
3. **Transition matrix estimation** — Dirichlet prior on rating transitions
4. **Recovery rate distribution** — beta prior, update with observed recoveries
5. **Spread forecast uncertainty** — full predictive distribution, not just point forecast

## Protocol
1. Define likelihood + priors (weakly informative defaults)
2. Sample 4 chains × 2000 samples (1000 warmup)
3. Diagnose: all r_hat < 1.01, all ESS > 400, divergences = 0
4. If diagnostics fail: reparameterize (non-centered for hierarchical) or increase samples
5. Posterior predictive check: simulated data should look like observed
6. Report: posterior means, 94% HDI, key diagnostics

## Gotchas
- **Divergences** — signal geometry problems. Reparameterize or increase adapt_delta.
- **Low ESS** — chains not mixing well. Increase samples or reparameterize.
- **r_hat > 1.01** — chains haven't converged. Run longer or fix model.
- **Non-centered parameterization** — essential for hierarchical models with few groups.
- **Priors matter** — weakly informative is not uninformative. Check prior predictive.

## Interpretation
- **94% HDI** — 94% highest density interval (not 95% CI — different concept)
- **Posterior mean** — point estimate, but HDI shows uncertainty
- **WAIC/LOO lower** — better predictive performance (like AIC but Bayesian)

## References
- Gelman et al. "Bayesian Data Analysis" 3rd ed.
- PyMC documentation: https://www.pymc.io/
- ArviZ: https://arviz-devs.github.io/arviz/
