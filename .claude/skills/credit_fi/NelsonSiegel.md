---
name: nelson-siegel
description: Use when fitting yield curves or spread curves with a parsimonious model or extracting level, slope, curvature factors.
---

# NelsonSiegel

## When to Use
- Fitting yield curves or spread curves with a parsimonious model.
- Interpolating/extrapolating curves beyond observed maturities.
- Extracting level, slope, curvature factors.

## Packages
```python
from scipy.optimize import minimize
import numpy as np
```

## Mathematical Background
$y(\tau) = \beta_0 + \beta_1 \frac{1-e^{-\tau/\lambda}}{\tau/\lambda} + \beta_2 \left(\frac{1-e^{-\tau/\lambda}}{\tau/\lambda} - e^{-\tau/\lambda}\right)$

- $\beta_0$: long-run level
- $\beta_1$: slope (short vs long end)
- $\beta_2$: curvature (hump)
- $\lambda$: decay parameter (where curvature peaks)

Svensson extension adds second hump term.

## Corresponding Script
`/scripts/credit_fi/nelson_siegel.py`
- `fit_nelson_siegel(maturities, yields) -> NSResult`
- `fit_svensson(maturities, yields) -> NSResult`
- `evaluate_curve(result, maturities) -> np.ndarray`

## Gotchas
1. **λ optimization is tricky.** Non-convex. Try grid search over λ ∈ [0.5, 5.0], then refine.
2. **Svensson overfits with few points.** Need ≥ 8 maturities. Use NS for fewer.
3. **Negative forward rates.** Can happen at long end. Check `f(t) = y(t) + t × y'(t) ≥ 0`.

## References
- Nelson & Siegel (1987). Parsimonious modeling of yield curves.
- Diebold & Li (2006). Forecasting the term structure of government bond yields.
