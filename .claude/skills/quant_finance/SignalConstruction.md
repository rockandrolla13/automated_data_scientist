---
name: signal-construction
description: Use when building trading signals from raw data including momentum, mean-reversion, carry, or value factors.
---

# SignalConstruction

## When to Use
- Building trading signals from raw data: momentum, mean-reversion, carry, value.
- Z-score normalization, cross-sectional ranking, signal combination.
- Feature engineering for ML models.

## Packages
```python
import pandas as pd
import numpy as np
from scipy import stats
```

## Corresponding Script
`/scripts/quant_finance/signal_construction.py`
- `momentum_signal(prices, lookback) -> pd.Series`
- `mean_reversion_signal(series, window, z_threshold) -> pd.Series`
- `zscore_normalize(signal, window) -> pd.Series`
- `combine_signals(signals, weights, method) -> pd.Series`
- `rank_signal(signal) -> pd.Series` — cross-sectional percentile rank

## Gotchas
1. **Normalize before combining.** Raw signal magnitudes differ. Z-score each first.
2. **Lookback window is a hyperparameter.** Don't optimize on test set.
3. **Signal decay.** Most signals lose power beyond 5–10 days. Check IC at multiple horizons.
4. **Turnover.** High-frequency signals have high turnover → costs erode alpha.

## References
- Kakushadze (2016). 101 Formulaic Alphas.
