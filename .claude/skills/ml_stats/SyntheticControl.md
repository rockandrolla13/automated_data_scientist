# SyntheticControl

## When to Use
- Single treated unit, multiple control units. Classic: "what if X didn't happen?"
- Policy/event impact with no parallel-trends assumption (unlike DiD).
- Credit: impact of rating downgrade on a specific issuer's spreads.

## Packages
```python
from sklearn.linear_model import LassoCV
import cvxpy as cp  # for constrained optimization
```

## Corresponding Script
`/scripts/ml_stats/synthetic_control.py`
- `fit_synthetic_control(treated, donors, pre_end) -> SyntheticControlResult`
- `placebo_test(donors, pre_end) -> pd.DataFrame` — leave-one-out placebo

## Gotchas
1. **Weights must be non-negative and sum to 1.** Constrained optimization, not OLS.
2. **Pre-treatment fit must be good.** If synthetic doesn't match pre-period, results are unreliable.
3. **Few donors = sparse solution.** Need ≥ 5 donor units for credible results.
4. **Placebo tests are mandatory.** Run on each donor as "fake treated" to gauge significance.

## References
- Abadie et al. (2010). Synthetic Control Methods for Comparative Case Studies.
