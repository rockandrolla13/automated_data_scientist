---
name: liquidity-scorer
description: Use when ranking assets by liquidity for trade execution or building liquidity factors for spread models.
---

# LiquidityScorer

## When to Use
- Ranking bonds/assets by liquidity for trade execution.
- Building liquidity factors for spread models.
- Filtering universe: only include bonds with sufficient liquidity.

## Packages
```python
import pandas as pd
import numpy as np
```

## Corresponding Script
`/scripts/quant_finance/liquidity_scorer.py`
- `amihud_illiquidity(returns, volume, window) -> pd.Series`
- `bid_ask_spread_proxy(high, low, close) -> pd.Series` — Corwin-Schultz estimator
- `composite_score(metrics, weights) -> pd.Series`

## Gotchas
1. **Bond liquidity ≠ equity liquidity.** Bonds trade OTC. Volume data is patchy.
2. **Amihud is noisy daily.** Use rolling 20-day average.
3. **New issues are liquid, old issues aren't.** Age since issuance is a strong predictor.

## References
- Amihud (2002). Illiquidity and stock returns.
- Corwin & Schultz (2012). A simple way to estimate bid-ask spreads from daily high and low prices.
