---
name: arima-forecasting
description: Use when forecasting stationary or trend-stationary univariate time series as a baseline before ML approaches.
---

# ARIMA

## When to Use
- Forecasting stationary or trend-stationary univariate series.
- Granger causality tests (requires VAR, which builds on ARIMA logic).
- Baseline forecast model before trying ML approaches.

## Packages
```python
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import acf, pacf
import pmdarima as pm  # auto_arima
```

## Mathematical Background
ARIMA(p,d,q): $\phi(B)(1-B)^d X_t = \theta(B)\epsilon_t$

- p: AR order (PACF cutoff)
- d: differencing order (ADF test)
- q: MA order (ACF cutoff)

SARIMAX adds seasonal + exogenous terms.

## Corresponding Script
`/scripts/ml_stats/arima.py`
- `fit_arima(series, order, seasonal_order) -> ARIMAResult`
- `auto_select_order(series, max_p, max_q) -> tuple` — uses pmdarima
- `granger_causality(df, target, cause, maxlag) -> pd.DataFrame`

## Gotchas
1. **Stationarity first.** Run ADF/KPSS (EDA skill) before fitting. Non-stationary → d=1.
2. **auto_arima is slow** on long series. Cap at `max_p=5, max_q=5`.
3. **Don't difference returns.** Returns are usually I(0). Prices are I(1). Differencing returns = over-differencing.
4. **Granger causality ≠ causation.** It tests predictive content, not mechanism.

## Interpretation Guide
| Output | Good sign | Bad sign |
|--------|-----------|----------|
| Residual ACF | All within blue bands | Spikes at lags → model mis-specified |
| Ljung-Box p | > 0.05 | < 0.05 → residuals autocorrelated |
| AIC comparison | Lower = better | — |

## References
- Box & Jenkins (1976). Time Series Analysis.
- pmdarima: https://alkaline-ml.com/pmdarima/
