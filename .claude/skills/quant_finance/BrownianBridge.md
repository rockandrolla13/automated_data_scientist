---
name: brownian-bridge
description: Monte Carlo simulation with pinned endpoints. Use for bond pricing paths, default time simulation, and variance reduction.
---

# Brownian Bridge — Constrained Path Simulation

## When to Use
- Bond pricing with known terminal value (par at maturity)
- Default time simulation in structural models (Merton, first-passage)
- Variance reduction in Monte Carlo (stratify on terminal value)
- Path-dependent options where terminal is known
- Interpolating yield curves with uncertainty

## Packages
- `numpy` — vectorized simulation
- `scipy.stats` — normal distributions

## Functions (scripts/quant_finance/brownian_bridge.py)

### `sample_bridge(t_start, t_end, x_start, x_end, n_steps, n_paths)`
Sample Brownian bridge paths from x_start to x_end. Returns array of shape (n_paths, n_steps+1).

### `sample_gbm_bridge(S0, ST, T, r, sigma, n_steps, n_paths)`
Geometric Brownian motion bridge — log-space bridge for asset prices.

### `default_time_simulation(V0, D, sigma, r, T, n_paths)`
Simulate first-passage times for Merton model. Returns DefaultTimeResult with default times and probabilities.

### `bond_path_simulation(P0, par, T, r, sigma, n_steps, n_paths)`
Simulate bond price paths pinned to par at maturity.

## Math Background
Brownian bridge B(t) from x₀ at t=0 to xₜ at t=T:
$$B(t) = x_0 + \frac{t}{T}(x_T - x_0) + W(t) - \frac{t}{T}W(T)$$

Or equivalently, condition W(T) = xₜ - x₀:
$$B(t) | W(T)=a \sim N\left(x_0 + \frac{t}{T}a, \frac{t(T-t)}{T}\right)$$

## Finance Use Cases
1. **Bond pricing** — simulate paths that end at par, compute path-dependent features
2. **Merton default** — first-passage time when asset value hits debt threshold
3. **Variance reduction** — stratify terminal values, bridge to each stratum
4. **Yield curve sampling** — interpolate between observed maturities with uncertainty
5. **CVA simulation** — exposure paths conditioned on known payoffs

## Protocol
1. Define start/end constraints (e.g., bond price today → par at maturity)
2. Choose n_paths (1000-10000 typical) and n_steps (daily for bonds)
3. Generate bridges
4. Compute path statistics or path-dependent payoffs
5. Report: mean, std, quantiles

## Gotchas
- **GBM bridge** — work in log-space, exponentiate after
- **First-passage** — check at every step, not just terminal
- **Variance** — bridge variance is t(T-t)/T, peaks at t=T/2
- **Negative prices** — GBM prevents this, but simple bridge doesn't

## Interpretation
- Bridge paths are **conditional** on endpoints — they're not forecasts
- Use for: "given we know the bond matures at par, what's the path distribution?"
- Don't use for: "where will the price be at maturity?"

## References
- Glasserman "Monte Carlo Methods in Financial Engineering" Ch. 3
- Merton (1974) "On the Pricing of Corporate Debt"
