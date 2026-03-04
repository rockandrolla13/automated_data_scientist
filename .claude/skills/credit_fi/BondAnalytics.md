# BondAnalytics

## When to Use
- Computing bond price, yield, duration, convexity from cash flows.
- Accrued interest, dirty/clean price conversion.
- Scenario analysis: price impact of yield changes.

## Packages
```python
import numpy as np
from scipy.optimize import brentq
```

## Mathematical Background
$P = \sum_{i=1}^n \frac{C_i}{(1+y/2)^{2t_i}}$. Duration: $D = -\frac{1}{P}\frac{dP}{dy}$.
Modified duration: $D_{mod} = D/(1+y/2)$. Convexity: $C = \frac{1}{P}\frac{d^2P}{dy^2}$.
Price change: $\Delta P \approx -D_{mod} \cdot \Delta y + \frac{1}{2} C \cdot (\Delta y)^2$.

## Corresponding Script
`/scripts/credit_fi/bond_analytics.py`
- `price_bond(face, coupon, maturity, ytm, freq) -> float`
- `ytm_from_price(price, face, coupon, maturity, freq) -> float`
- `duration_convexity(face, coupon, maturity, ytm, freq) -> BondMetrics`
- `scenario_analysis(bond, yield_shocks) -> pd.DataFrame`

## Gotchas
1. **Day count convention.** 30/360 for corporates, ACT/ACT for govies. Specify explicitly.
2. **Frequency.** US corporates = semi-annual (freq=2). Euros = annual (freq=1).
3. **Pull-to-par.** Duration changes as bond approaches maturity. Recompute, don't cache.

## References
- Fabozzi (2007). Fixed Income Analysis, Ch. 4–5.
