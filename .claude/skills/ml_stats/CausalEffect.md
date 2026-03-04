# CausalEffect

## When to Use
- Estimating causal impact of an intervention (policy change, event, structural break).
- DAG-based causal reasoning: identifying confounders, mediators, colliders.
- When correlation ≠ causation and you need to formalize assumptions.

## Packages
```python
import dowhy
from dowhy import CausalModel
```

## Mathematical Background
Potential outcomes framework: ATE = E[Y(1) - Y(0)].
DoWhy workflow: Model → Identify → Estimate → Refute.
Methods: IPW, matching, instrumental variables, regression discontinuity.

## Corresponding Script
`/scripts/ml_stats/causal_effect.py`
- `estimate_ate(df, treatment, outcome, confounders, method) -> CausalResult`
- `refute_estimate(result, method) -> RefutationResult`

## Gotchas
1. **DAG must be specified.** DoWhy requires explicit causal graph. No graph → no identification.
2. **Unobserved confounders kill everything.** Always run sensitivity analysis (E-value).
3. **Positivity assumption.** Every unit must have nonzero probability of treatment.
4. **Refutation tests are mandatory.** Random common cause, placebo treatment, data subset.

## Interpretation Guide
- ATE estimate + 95% CI → does CI exclude zero?
- Refutation p-value > 0.05 → estimate survives the challenge.

## References
- Pearl (2009). Causality.
- DoWhy: https://www.pywhy.org/dowhy/
