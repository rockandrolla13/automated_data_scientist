---
name: etf-premium-discount
description: Use when measuring ETF premium/discount to NAV or identifying arbitrage and liquidity stress in credit ETFs.
---

# ETFPremiumDiscount

## When to Use
- Measuring ETF premium/discount to NAV.
- Identifying arbitrage or liquidity stress in credit ETFs (LQD, HYG, JNK).
- Intraday indicative value vs market price analysis.

## Packages
```python
import pandas as pd
import numpy as np
```

## Corresponding Script
`/scripts/credit_fi/etf_premium_discount.py`
- `compute_premium(price, nav) -> pd.Series` — (price - NAV) / NAV in bps
- `rolling_premium_stats(premium, window) -> pd.DataFrame`
- `detect_stress_episodes(premium, threshold_bps) -> pd.DataFrame`

## Gotchas
1. **Stale NAV.** NAV is end-of-day. Intraday premium uses iNAV, which can also be stale for illiquid bonds.
2. **Authorized participant activity.** Large premiums/discounts trigger creation/redemption. Persistent premium = structural.
3. **Credit ETF specifics.** Bond ETFs trade more liquid than underlyings. Premium can reflect information, not mispricing.

## References
- Pan & Zeng (2019). ETF Arbitrage under Liquidity Mismatch.
