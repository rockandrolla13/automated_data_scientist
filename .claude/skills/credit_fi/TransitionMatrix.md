---
name: transition-matrix
description: Use when estimating rating migration probabilities or computing multi-period transition matrices for stress testing.
---

# TransitionMatrix

## When to Use
- Estimating rating migration probabilities (AAA→AA, BBB→default, etc.).
- Multi-period transition: T-year matrix from 1-year via matrix power.
- Stress testing: what if downgrade probabilities double?

## Packages
```python
import numpy as np
from scipy.linalg import expm, logm
```

## Mathematical Background
Generator matrix $Q$: $P(t) = e^{Qt}$. Rows sum to 0, off-diag ≥ 0.
Cohort method: count transitions $n_{ij}$ over period, $\hat{p}_{ij} = n_{ij}/n_i$.
Duration method: continuous-time estimation, handles withdrawn ratings.

## Corresponding Script
`/scripts/credit_fi/transition_matrix.py`
- `estimate_cohort(ratings_start, ratings_end, states) -> np.ndarray`
- `multi_period(P, years) -> np.ndarray` — P^n via eigendecomposition
- `generator_from_transition(P) -> np.ndarray` — extract Q from P
- `stressed_matrix(P, stress_factor) -> np.ndarray` — scale off-diagonal migration probs

## Gotchas
1. **Absorbing state.** Default is absorbing (row = [0,...,0,1]). Enforce this.
2. **Negative generator entries.** `logm(P)` can produce negatives. Use regularization.
3. **Small samples per cell.** AAA→CCC transitions are rare. Don't trust n < 5 in any cell.
4. **Through-the-cycle vs point-in-time.** Agency matrices are TTC. Market-implied are PIT.

## References
- Lando & Skødeberg (2002). Analyzing rating transitions and rating drift with continuous observations.
- Jarrow, Lando & Turnbull (1997). A Markov model for the term structure of credit risk spreads.
