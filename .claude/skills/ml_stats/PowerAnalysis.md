# PowerAnalysis

## When to Use
- Before running an experiment: how much data do you need?
- After a null result: was the test underpowered?
- Designing A/B tests, clinical trials, signal backtests.

## Packages
```python
from statsmodels.stats.power import TTestIndPower, NormalIndPower
import pingouin as pg
```

## Mathematical Background
Power = P(reject H₀ | H₁ true). Convention: target 80%.
Inputs: effect size (Cohen's d), α, power → outputs required n.
$n = \left(\frac{z_{1-\alpha/2} + z_{1-\beta}}{d}\right)^2$

## Corresponding Script
`/scripts/ml_stats/power_analysis.py`
- `required_sample_size(effect_size, alpha, power) -> int`
- `achieved_power(effect_size, n, alpha) -> float`
- `power_curve(effect_sizes, n, alpha) -> pd.DataFrame`

## Gotchas
1. **Effect size is the hard part.** Use pilot data or domain knowledge. Don't guess.
2. **Two-sided vs one-sided.** Most tests are two-sided. One-sided needs justification.
3. **Sharpe ratio as effect size.** SR = mean/std ≈ Cohen's d per √n observations.
4. **Underpowered study ≠ no effect.** It means you can't tell.

## References
- Cohen (1988). Statistical Power Analysis for the Behavioral Sciences.
