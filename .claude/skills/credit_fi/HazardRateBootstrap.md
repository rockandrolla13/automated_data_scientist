# HazardRateBootstrap

## When to Use
- Extracting implied hazard rates (default intensities) from CDS spreads.
- Building a term structure of default probability from market data.
- Pricing off-market CDS or computing CVA.

## Packages
```python
import numpy as np
from scipy.optimize import brentq
from scipy.interpolate import PchipInterpolator
```

## Mathematical Background
CDS spread = $s$ compensates for expected loss. Under constant hazard $\lambda$ between knots:
$\text{Protection Leg} = \text{Premium Leg}$ solved for $\lambda$.
Survival probability: $Q(t) = e^{-\int_0^t \lambda(u) du}$.
Piecewise-constant bootstrap: solve for $\lambda_i$ at each CDS tenor sequentially.

## Corresponding Script
`/scripts/credit_fi/hazard_rate_bootstrap.py`
- `bootstrap_hazard_rates(tenors, spreads, recovery, discount_curve) -> HazardResult`
- `survival_probability(hazard_result, t) -> float`
- `fair_spread(hazard_result, tenor, recovery) -> float`

## Gotchas
1. **Bootstrap sequentially.** 1Y first, then 3Y, 5Y, 7Y, 10Y. Each step uses prior lambdas.
2. **Recovery assumption.** Standard = 40% for senior unsecured. Changes everything.
3. **Negative hazard rates.** Can happen with inverted CDS curves. Cap at 0 or flag.
4. **Discount curve matters.** Use OIS/SOFR, not LIBOR/Treasury.

## References
- O'Kane (2008). Modelling Single-name and Multi-name Credit Derivatives, Ch. 5.
