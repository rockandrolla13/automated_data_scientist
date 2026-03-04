---
name: vectorbt-backtest
description: Use when running high-performance vectorized backtests or parameter sweeps across thousands of combinations.
---

# Vectorbt

## When to Use
- High-performance vectorized backtesting (orders of magnitude faster than loops).
- Parameter sweeps: testing 1000s of parameter combinations.
- Built-in portfolio analytics, Sharpe, drawdown, returns.

## Packages
```python
import vectorbt as vbt
```

## Corresponding Script
`/scripts/quant_finance/vectorbt.py`
- `run_vbt_backtest(close, entries, exits, fees) -> VBTResult`
- `parameter_sweep(close, param_grid) -> pd.DataFrame`
- `plot_vbt_results(portfolio, path)` — equity curve, drawdowns

## Gotchas
1. **Boolean signals.** vbt uses True/False entry/exit arrays, not position sizes. Convert first.
2. **freq parameter.** Must match data frequency for correct annualization. `freq="1D"` for daily.
3. **Memory.** Parameter sweeps with 10k+ combos can OOM. Batch them.
4. **No short-selling by default.** Set `direction="both"` for long/short.

## References
- vectorbt: https://vectorbt.dev/
