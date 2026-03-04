# PortfolioOptimizer

## When to Use
- Mean-variance optimization, minimum variance, max Sharpe.
- Weight constraints: long-only, max position size, sector limits.
- Robust optimization: shrinkage estimators, resampled frontiers.

## Packages
```python
import cvxpy as cp
import numpy as np
```

## Mathematical Background
$\min_w \frac{1}{2} w^T \Sigma w - \lambda \mu^T w$ s.t. $\mathbf{1}^T w = 1$, $w \geq 0$.

## Corresponding Script
`/scripts/quant_finance/portfolio_optimizer.py`
- `mean_variance(mu, Sigma, risk_aversion, constraints) -> PortfolioResult`
- `min_variance(Sigma, constraints) -> PortfolioResult`
- `max_sharpe(mu, Sigma, rf, constraints) -> PortfolioResult`
- `efficient_frontier(mu, Sigma, n_points) -> pd.DataFrame`

## Gotchas
1. **Estimation error dominates.** Sample covariance is noisy. Use Ledoit-Wolf shrinkage.
2. **Extreme weights.** Unconstrained MVO produces wild weights. Add max weight constraint (e.g., 10%).
3. **Rebalancing frequency.** Monthly > daily for most strategies. Higher freq = more costs.
4. **CVXPY solver.** Default OSQP is fast. Use SCS for large problems.

## References
- Markowitz (1952). Portfolio Selection.
- Ledoit & Wolf (2004). Honey, I Shrunk the Sample Covariance Matrix.
