# OpenBB

## When to Use
- Accessing free financial data: equity prices, macro, crypto, forex.
- Alternative to Bloomberg for personal/research use.
- Rapid data exploration across asset classes.

## Packages
```python
# pip install openbb (heavy, install on demand)
from openbb import obb
```

## Corresponding Script
`/scripts/quant_finance/openbb.py`
- `get_equity_prices(symbol, start, end) -> pd.DataFrame`
- `get_macro_data(series, start, end) -> pd.DataFrame`
- `get_etf_holdings(symbol) -> pd.DataFrame`

## Gotchas
1. **Heavy install.** ~2GB. Install in separate venv or on demand.
2. **API keys required** for premium data (Polygon, FMP). Free sources have limits.
3. **Data quality varies** by provider. Cross-check critical data.
4. **Breaking changes.** OpenBB API changes frequently between versions. Pin version.

## References
- OpenBB: https://docs.openbb.co/
