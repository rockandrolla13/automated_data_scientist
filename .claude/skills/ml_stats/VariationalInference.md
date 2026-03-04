---
name: variational-inference
description: Fast approximate Bayesian inference via optimization. Use when MCMC is too slow or for quick iteration on model structure.
---

# Variational Inference — Fast Approximate Posteriors

## When to Use
- Dataset too large for MCMC (n > 100k)
- Need quick approximate posteriors for iteration
- Online/streaming Bayesian updates
- Initial exploration before full MCMC
- Deep generative models (VAEs)

## Packages
- `pymc>=5.10` — ADVI implementation
- `numpyro>=0.14` — fast JAX-native SVI

## Functions (scripts/ml_stats/variational_inference.py)

### `fit_advi(model_fn, data, n_iter=30000)`
Mean-field ADVI. Assumes independent posterior factors. Fast but may underestimate uncertainty.

### `fit_fullrank_advi(model_fn, data, n_iter=50000)`
Full-rank ADVI. Captures posterior correlations but slower.

### `compare_vi_mcmc(vi_result, mcmc_trace)`
Compare VI approximation to MCMC ground truth. Returns divergence metrics.

### `sample_from_vi(vi_result, n_samples)`
Draw samples from fitted variational approximation.

## Math Background
VI turns inference into optimization. Find q*(θ) that minimizes KL divergence to true posterior:
$$q^*(\theta) = \arg\min_{q \in \mathcal{Q}} \text{KL}(q(\theta) \| p(\theta|D))$$

Equivalent to maximizing the Evidence Lower Bound (ELBO):
$$\text{ELBO} = \mathbb{E}_q[\log p(D|\theta)] - \text{KL}(q(\theta) \| p(\theta))$$

## Mean-Field vs Full-Rank
- **Mean-field**: q(θ) = ∏ q(θᵢ). Fast, but assumes independence → underestimates posterior variance.
- **Full-rank**: q(θ) = N(μ, Σ). Captures correlations but O(d²) parameters.

## Finance Use Cases
1. **Large-scale credit models** — millions of loans, too slow for MCMC
2. **Online spread forecasting** — update beliefs as new data arrives
3. **Quick model comparison** — screen many models before full MCMC on finalists
4. **Hierarchical models** — mean-field often sufficient for large hierarchies

## Protocol
1. Start with mean-field ADVI (fast)
2. Check ELBO convergence (should plateau)
3. If posterior correlations matter: switch to full-rank
4. Validate against MCMC on subset if possible
5. Report: approximate posterior means, sds (not HDI — VI gives approximate normal)

## Gotchas
- **Underestimates uncertainty** — VI posteriors are often too narrow
- **Mode-seeking** — may miss multimodal posteriors (picks one mode)
- **ELBO noise** — use moving average to assess convergence
- **Not a substitute for MCMC** — use for exploration, confirm with MCMC for final results

## MCMC vs VI Decision
| Factor | MCMC | VI |
|--------|------|-----|
| n < 10k | ✓ | |
| n > 100k | | ✓ |
| Need exact posterior | ✓ | |
| Quick iteration | | ✓ |
| Multimodal posterior | ✓ | |
| Production/streaming | | ✓ |

## References
- Blei et al. "Variational Inference: A Review for Statisticians"
- Kucukelbir et al. "Automatic Differentiation Variational Inference"
