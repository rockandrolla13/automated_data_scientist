# CreditSignals

## When to Use
- Building credit-specific trading signals: spread momentum, carry, value, quality.
- Cross-sectional signals: rank issuers by signal, go long cheap / short rich.
- Combining credit signals with macro conditions.

## Packages
```python
import pandas as pd
import numpy as np
```

## Corresponding Script
`/scripts/quant_finance/credit_signals.py`
- `spread_momentum(spreads, lookback) -> pd.Series`
- `carry_signal(spreads, funding_rate) -> pd.Series`
- `value_signal(spreads, fair_spread) -> pd.Series` — deviation from fair value
- `quality_signal(ratings, leverage, coverage) -> pd.Series`
- `composite_credit_signal(signals, weights) -> pd.Series`

## Gotchas
1. **Spread momentum is contrarian at extremes.** Momentum works in normal times, reverts in stress.
2. **Carry is mechanical.** High spread = high carry. But also high default risk. Adjust for PD.
3. **Cross-sectional signals need universe control.** Compare within same rating bucket.
4. **Signal decay is faster in credit** than equity. IC drops after 5d for most signals.

## References
- Israel, Palhares & Richardson (2018). Common factors in corporate bond returns.
- Houweling & Van Zundert (2017). Factor investing in the corporate bond market.
