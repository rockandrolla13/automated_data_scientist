---
name: garch-volatility
description: Use when modeling time-varying volatility, VaR/ES estimation, or comparing volatility model specifications.
---

# GARCH

## When to Use
- Modeling time-varying volatility (heteroskedasticity).
- VaR/ES estimation. Volatility forecasting. Risk-return tradeoffs (GARCH-M).
- Comparing vol models: GARCH, EGARCH, GJR-GARCH, TGARCH.

## Packages
```python
from arch import arch_model
from arch.univariate import GARCH, EGARCH, ConstantMean, ZeroMean
```
**Install:** `pip install arch`

## Mathematical Background
GARCH(p,q): $\sigma_t^2 = \omega + \sum_{i=1}^q \alpha_i \epsilon_{t-i}^2 + \sum_{j=1}^p \beta_j \sigma_{t-j}^2$

Persistence: $\alpha + \beta$. If ≥ 1, integrated (IGARCH). Typical range: 0.95–0.99.

EGARCH adds asymmetry: negative shocks → larger vol increase (leverage effect).

## Corresponding Script
`/scripts/ml_stats/garch.py`
- `fit_garch(returns, p, q, model_type, dist) -> GARCHResult`
- `forecast_vol(result, horizon) -> pd.DataFrame`
- `compare_models(returns, models) -> pd.DataFrame`

## Gotchas
1. **Returns, not prices.** GARCH operates on returns. Use percentage returns (×100) for `arch`.
2. **Convergence failures.** Try different optimizers: `method="Nelder-Mead"` if L-BFGS fails.
3. **Student-t > Normal.** Financial returns have fat tails. Always try `dist="t"` or `"skewt"`.
4. **Persistence near 1.** Common. Not necessarily a problem — just means vol is very persistent.
5. **arch uses percentage returns.** If your returns are decimal (0.01), multiply by 100.

## Interpretation Guide
| Parameter | Meaning | Typical range |
|-----------|---------|---------------|
| ω (omega) | Long-run variance floor | Small positive |
| α (alpha) | Shock impact | 0.05–0.15 |
| β (beta) | Persistence | 0.80–0.95 |
| α+β | Total persistence | 0.95–0.99 |
| ν (nu, for t-dist) | Tail thickness | 4–10 (lower = fatter) |

## References
- Bollerslev (1986). Generalized autoregressive conditional heteroskedasticity.
- Hansen & Lunde (2005). A forecast comparison of volatility models.
- `arch` docs: https://arch.readthedocs.io/
