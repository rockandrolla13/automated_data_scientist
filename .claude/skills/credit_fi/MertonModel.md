---
name: merton-model
description: Use when estimating default probability from equity prices and balance sheet data or computing distance-to-default.
---

# MertonModel

## When to Use
- Estimating default probability from equity prices + balance sheet data.
- Structural credit risk modeling: distance-to-default, implied asset vol.
- Fair-value CDS spread estimation.

## Packages
```python
from scipy.optimize import fsolve
from scipy.stats import norm
import numpy as np
```

## Mathematical Background
Firm value: $V_t \sim GBM(\mu, \sigma_V)$. Equity = call on assets: $E = V N(d_1) - D e^{-rT} N(d_2)$.
$d_1 = \frac{\ln(V/D) + (r + \sigma_V^2/2)T}{\sigma_V\sqrt{T}}$, $d_2 = d_1 - \sigma_V\sqrt{T}$.
Distance-to-default: $DD = \frac{\ln(V/D) + (\mu - \sigma_V^2/2)T}{\sigma_V\sqrt{T}}$.
Default probability: $PD = N(-DD)$.

System of 2 equations (equity value + equity vol) solved for 2 unknowns ($V$, $\sigma_V$).

## Corresponding Script
`/scripts/credit_fi/merton_model.py`
- `solve_merton(equity, equity_vol, debt, r, T) -> MertonResult`
- `distance_to_default(V, debt, mu, sigma_V, T) -> float`
- `implied_spread(pd, lgd, T) -> float` — PD × LGD / duration approximation

## Gotchas
1. **fsolve needs good initial guess.** Start with V₀ = E + D, σ_V₀ = σ_E × E/V₀.
2. **Debt maturity assumption matters.** KMV uses weighted avg of short + 0.5 × long-term debt.
3. **Real-world vs risk-neutral PD.** Merton gives risk-neutral PD. For real-world, adjust drift to μ.
4. **Low-leverage firms.** DD → ∞, PD → 0. Model is insensitive for high-quality credits.
5. **Negative equity vol.** Can't happen. If solver returns σ_V < 0, initial guess is wrong.

## Interpretation Guide
| DD | PD (approx) | Rating equivalent |
|----|-------------|-------------------|
| > 4 | < 0.003% | AAA/AA |
| 3–4 | 0.01–0.1% | A |
| 2–3 | 0.1–1% | BBB |
| 1–2 | 1–10% | BB/B |
| < 1 | > 15% | CCC or below |

## References
- Merton (1974). On the pricing of corporate debt.
- Crosbie & Bohn (2003). Modeling default risk (KMV).
