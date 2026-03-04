# DataLoading

## When to Use
- Loading CSV, Parquet, Excel, JSON into pandas/polars.
- Downloading from FRED, Yahoo Finance, or OpenBB.
- Standardizing column names, dtypes, and index before analysis.

## Packages
```python
import pandas as pd
import pyarrow.parquet as pq
```
Optional: `fredapi`, `yfinance`, `openbb`

## Corresponding Script
`/scripts/infrastructure/data_loading.py`
- `load_file(path) -> pd.DataFrame` — auto-detect format, parse dates, set index
- `load_fred(series_ids, start, end) -> pd.DataFrame` — FRED API wrapper
- `standardize_columns(df) -> pd.DataFrame` — lowercase, underscores, strip whitespace

## Gotchas
1. **Parquet preserves dtypes.** CSV doesn't. Always save intermediate data as Parquet.
2. **Timezone-naive convention.** Strip timezones on load: `df.index = df.index.tz_localize(None)`.
3. **FRED rate limits.** 120 requests/minute. Batch series IDs in one call.
4. **Excel dates.** `pd.read_excel` can misparse dates. Always specify `parse_dates` explicitly.

## Interpretation Guide
N/A — utility skill. Success = DataFrame loads with correct dtypes, DatetimeIndex, no surprises.

## References
- Pandas I/O: https://pandas.pydata.org/docs/user_guide/io.html
- PyArrow: https://arrow.apache.org/docs/python/
