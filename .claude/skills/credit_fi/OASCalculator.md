# OASCalculator

## When to Use
- Computing option-adjusted spread for callable/putable bonds.
- Comparing bonds with embedded options on a like-for-like basis.
- OAS = Z-spread adjusted for optionality.

## Packages
```python
import numpy as np
from scipy.optimize import brentq
```

## Mathematical Background
OAS: constant spread added to each node of an interest rate tree such that model price = market price.
For non-callable bonds, OAS ≈ Z-spread.
$P_{market} = \sum_i \frac{CF_i}{\prod_{j=1}^i (1 + r_j + OAS)}$ solved for OAS.

## Corresponding Script
`/scripts/credit_fi/oas_calculator.py`
- `z_spread(price, cash_flows, discount_curve) -> float`
- `oas_from_tree(price, cash_flows, rate_tree, call_schedule) -> float`
- `spread_duration(price, cash_flows, discount_curve, oas) -> float`

## Gotchas
1. **Need an interest rate model** for callable bonds. BDT or Hull-White. Z-spread is not OAS for callables.
2. **Negative OAS is possible** if bond trades above model price (very rare, usually data error).
3. **Spread duration ≠ modified duration** for callables. Use OAS-based DV01.

## References
- Fabozzi (2007). Fixed Income Analysis, Ch. 9.
