---
name: mcmc
description: Run Bayesian inference on a model using MCMC. Full posterior estimation with diagnostics.
---

Run MCMC inference for: $ARGUMENTS

## Pipeline
1. **Read skill** — .claude/skills/ml_stats/MCMC.md

2. **Define model** — Specify likelihood and priors:
   - Likelihood: what distribution does the data follow?
   - Priors: weakly informative defaults (Normal(0, 5) for location, HalfNormal(2) for scale)
   - Write model function for scripts/ml_stats/mcmc.py

3. **Sample posterior**
   - 4 chains × 2000 samples (1000 warmup)
   - target_accept = 0.9 (increase to 0.95 if divergences)
   - `sample_posterior(model_fn, data)`

4. **Diagnose** — `diagnose_chains(trace)`. All must pass:
   - r_hat < 1.01 for all parameters
   - ESS > 400 for all parameters
   - divergences = 0
   - If any fail: reparameterize or increase samples

5. **Visualize**
   - Trace plots (chains should mix)
   - Posterior distributions with 94% HDI
   - Pair plots for correlated parameters
   - Save to experiment folder

6. **Posterior predictive check**
   - Generate predictions from posterior
   - Compare simulated data to observed
   - Do they look similar?

7. **Report**
   - Parameter estimates: mean, 94% HDI
   - Diagnostics summary
   - Model comparison (WAIC/LOO) if multiple models

8. **Save**
   - Trace to experiment folder (pickle or NetCDF)
   - Diagnostics to results.json
   - Figures to figures/

Example: /mcmc "estimate posterior on Merton model params for IG issuers"
