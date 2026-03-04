# DiffInDiff

## When to Use
- Estimating treatment effects with a control group and pre/post periods.
- Policy evaluation, event studies in credit markets.
- When randomization isn't possible but parallel trends assumption holds.

## Packages
```python
import statsmodels.formula.api as smf
```

## Mathematical Background
$Y_{it} = \alpha + \beta_1 \text{Treat}_i + \beta_2 \text{Post}_t + \delta(\text{Treat}_i \times \text{Post}_t) + \epsilon_{it}$

$\delta$ is the DiD estimator (the causal effect).

Parallel trends: absent treatment, treated and control groups would have followed the same trajectory.

## Corresponding Script
`/scripts/ml_stats/diff_in_diff.py`
- `fit_did(df, outcome, treat_col, post_col) -> DIDResult`
- `event_study(df, outcome, treat_col, time_col, event_time) -> pd.DataFrame`

## Gotchas
1. **Parallel trends must be tested.** Plot pre-treatment trends. If diverging, DiD is invalid.
2. **Cluster standard errors** by unit if panel data. Use `cov_type="cluster"`.
3. **Staggered treatment** requires modern DiD (Callaway-Sant'Anna or Sun-Abraham), not basic 2×2.

## References
- Angrist & Pischke (2009). Mostly Harmless Econometrics, Ch. 5.
- Callaway & Sant'Anna (2021). Difference-in-Differences with Multiple Time Periods.
