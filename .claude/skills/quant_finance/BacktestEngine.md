# BacktestEngine

## When to Use
- Running strategy backtests: signal → position → PnL.
- Walk-forward evaluation after initial 60/20/20 split.
- Transaction cost analysis, turnover measurement.

## Packages
```python
import numpy as np
import pandas as pd
```

## Corresponding Script
`/scripts/quant_finance/backtest_engine.py`
- `backtest(signals, returns, costs_bps) -> BacktestResult`
- `walk_forward(signals, returns, train_window, test_window) -> pd.DataFrame`
- `compute_metrics(returns_series) -> dict` — Sharpe, MDD, IR, t-stat

## Gotchas
1. **Signals are t, returns are t+1.** Signal at close on day t → return from close t to close t+1. Off-by-one = look-ahead.
2. **Transaction costs compound.** 5bps per trade × 250 trades/year = 125bps drag.
3. **Max drawdown is path-dependent.** Same final return can have very different drawdowns.
4. **Walk-forward ≠ cheating.** It's a more honest test than single split, but still uses all data. Report both.
5. **Slippage > commission** for illiquid bonds. Use 5–10bps for IG, 20–50bps for HY.

## Interpretation Guide
Apply §7 canonical metrics. If OOS Sharpe > IS Sharpe, explain why (or be suspicious).

## References
- De Prado (2018). Advances in Financial Machine Learning, Ch. 12.
