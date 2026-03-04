---
name: black-litterman
description: Use when incorporating subjective views into portfolio optimization or blending market equilibrium with analyst forecasts.
---

# BlackLitterman

## When to Use
- Incorporating subjective views into portfolio optimization.
- "I think IG will outperform HY by 50bps" → tilted weights.
- Blending market equilibrium with analyst forecasts.

## Packages
```python
import numpy as np
```

## Mathematical Background
Equilibrium excess returns: $\Pi = \delta \Sigma w_{mkt}$.
Combined return: $\mu_{BL} = [(\tau\Sigma)^{-1} + P^T \Omega^{-1} P]^{-1} [(\tau\Sigma)^{-1}\Pi + P^T \Omega^{-1} Q]$.
$P$ = pick matrix, $Q$ = view returns, $\Omega$ = view uncertainty.

## Corresponding Script
`/scripts/quant_finance/black_litterman.py`
- `black_litterman(Sigma, market_weights, views, view_confidences, tau) -> BLResult`
- `equilibrium_returns(Sigma, market_weights, delta) -> np.ndarray`

## Gotchas
1. **τ is small** (0.01–0.05). Larger τ → views dominate.
2. **Ω diagonal assumption.** Default = diagonal. Off-diagonal for correlated views.
3. **Market weights needed.** Use index weights as starting point.
4. **Views must be relative or absolute.** P matrix structure differs.

## References
- Black & Litterman (1992). Global portfolio optimization.
- He & Litterman (1999). The intuition behind Black-Litterman model portfolios.
