# EDA

## When to Use
- First touch on any dataset. Mandatory before hypotheses (§4 Step 1).
- No `_clean` version in `/data/`.
- Checking stationarity, nulls, outliers, distributions before modeling.

## Packages
```python
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.stattools import adfuller, kpss
import matplotlib.pyplot as plt
import seaborn as sns
```

## Corresponding Script
`/scripts/infrastructure/eda.py`
- `profile_dataframe(df) -> EDAReport` — full statistical profile
- `check_stationarity(series) -> StationarityResult` — ADF + KPSS
- `detect_outliers(series, method) -> OutlierResult` — IQR, z-score, or MAD
- `clean_dataframe(df, report) -> pd.DataFrame` — applies fixes, returns clean copy

## Gotchas
1. **ADF vs KPSS disagree.** ADF null=unit root, KPSS null=stationary. Both reject → trend-stationary, difference it.
2. **Don't drop outliers blindly.** In credit spreads, "outliers" are the signal. Flag, don't remove unless clearly erroneous.
3. **Forward-fill before returns.** Missing prices → ffill. Missing returns → drop. Log affected rows.
4. **Duplicate timestamps.** Common in tick data. Deduplicate by last or aggregate.
5. **ydata-profiling slow on >100k rows.** Use lightweight `profile_dataframe()` for large data.

## Interpretation Guide
| Output | Check | Action |
|--------|-------|--------|
| Null % per col | > 5% | Investigate, decide ffill/drop/interpolate |
| ADF p-value | < 0.05 → stationary | If not, difference |
| Skewness | \|skew\| > 2 | Log-transform or note fat tails |
| Kurtosis | excess > 6 | Use Student-t, not Normal |
| Duplicate timestamps | > 0 | Deduplicate |

## References
- ADF: Said & Dickey (1984)
- KPSS: Kwiatkowski et al. (1992)
