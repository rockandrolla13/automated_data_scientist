# HypothesisTesting

## When to Use
- Formal statistical tests: t-test, Mann-Whitney, KS, Kolmogorov-Smirnov.
- Multiple comparison correction (Bonferroni, BH-FDR).
- Comparing model performance across folds or regimes.

## Packages
```python
from scipy import stats
from statsmodels.stats.multitest import multipletests
import pingouin as pg
```

## Corresponding Script
`/scripts/ml_stats/hypothesis_testing.py`
- `two_sample_test(a, b, test, alternative) -> TestResult`
- `paired_test(a, b) -> TestResult`
- `multiple_test_correction(pvalues, method) -> CorrectedResult`

## Gotchas
1. **Multiple comparisons.** Testing 10 hypotheses at α=0.05 → expect 0.5 false positives. Always correct.
2. **Non-normal data.** Use Mann-Whitney or permutation tests if QQ-plot shows deviation.
3. **Effect size matters more than p-value.** Report Cohen's d alongside p.
4. **n < 30 → non-parametric.** Invariant 7 applies.

## Interpretation Guide
| p-value | Meaning | Action |
|---------|---------|--------|
| < 0.01 | Strong evidence against H₀ | Report as significant |
| 0.01–0.05 | Moderate evidence | Report, note marginal |
| 0.05–0.10 | Suggestive | Do not claim significance |
| > 0.10 | No evidence | Fail to reject H₀ |

## References
- Benjamini & Hochberg (1995). Controlling the false discovery rate.
- pingouin: https://pingouin-stats.org/
