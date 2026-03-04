---
name: risk-parity
description: Use when allocating so each asset contributes equally to portfolio risk or when expected returns are unreliable.
---

# RiskParity

## When to Use
- Allocating such that each asset contributes equally to portfolio risk.
- When expected returns are unreliable but covariance is estimable.
- Alternative to MVO for multi-asset portfolios.

## Packages
```python
from scipy.optimize import minimize
import numpy as np
```

## Mathematical Background
Risk contribution of asset i: $RC_i = w_i (\Sigma w)_i / \sigma_p$.
Risk parity: $RC_i = RC_j \ \forall i,j$.
Equivalent to: $\min_w \sum_i (w_i (\Sigma w)_i - \sigma_p^2/n)^2$.

## Corresponding Script
`/scripts/quant_finance/risk_parity.py`
- `risk_parity_weights(Sigma) -> RiskParityResult`
- `risk_contributions(weights, Sigma) -> np.ndarray`
- `hierarchical_risk_parity(returns) -> np.ndarray` — HRP via clustering

## Gotchas
1. **All positive semi-definite.** If Σ is not PSD, regularize.
2. **Leveraged.** Risk parity weights can sum to >1. Normalize or lever.
3. **HRP is more robust** than MVO-based risk parity. Use when Σ is noisy.

## References
- Maillard, Roncalli & Teïletche (2010). The properties of equally weighted risk contribution portfolios.
- De Prado (2016). Building diversified portfolios that outperform out-of-sample.
