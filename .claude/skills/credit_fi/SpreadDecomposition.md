# SpreadDecomposition

## When to Use
- Decomposing credit spreads into default risk + liquidity + residual.
- Identifying cheap/rich bonds relative to CDS (basis analysis).
- Understanding what drives spread changes.

## Packages
```python
import statsmodels.api as sm
import numpy as np
import pandas as pd
```

## Mathematical Background
$s_{it} = \alpha_i + \beta_1 \cdot PD_{it} + \beta_2 \cdot Liq_{it} + \beta_3 \cdot Macro_t + \epsilon_{it}$

Common decomposition: OAS = default component (CDS-implied) + liquidity premium + residual.
Basis = CDS spread − bond Z-spread. Positive basis = bond cheap vs CDS.

## Corresponding Script
`/scripts/credit_fi/spread_decomposition.py`
- `decompose_spread(spreads, cds, liquidity_proxy, macro) -> DecompResult`
- `compute_basis(cds_spread, bond_spread) -> pd.Series`
- `regime_decomposition(spreads, regimes) -> pd.DataFrame` — decompose within regimes

## Gotchas
1. **CDS-bond basis is not arbitrage-free.** Funding costs, delivery option, restructuring clauses create persistent basis.
2. **Liquidity proxy choice matters.** Bid-ask, turnover, or Amihud illiquidity. All are noisy.
3. **Multicollinearity.** Default risk and macro factors are correlated. Check VIF.

## References
- Longstaff, Mithal & Neis (2005). Corporate yield spreads: default risk or liquidity?
