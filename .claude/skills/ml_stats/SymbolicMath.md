# SymbolicMath

## When to Use
- Deriving closed-form solutions (option pricing, duration formulas).
- Verifying numerical results against analytical expressions.
- Symbolic differentiation for sensitivity analysis (Greeks, delta-method).

## Packages
```python
import sympy as sp
from sympy import symbols, diff, integrate, simplify, solve, exp, sqrt, log
```

## Corresponding Script
`/scripts/ml_stats/symbolic_math.py`
- `derive_greeks(option_formula, params) -> dict` — symbolic derivatives
- `solve_equation(expr, variable) -> list` — symbolic solver
- `latex_display(expr) -> str` — LaTeX string for reports

## Gotchas
1. **sympy is slow for large expressions.** Simplify aggressively.
2. **Numerical evaluation.** Use `expr.evalf(subs={x: 1.5})` to get a number.
3. **Assumptions matter.** `symbols('x', positive=True)` affects simplification.
4. **Don't use for numerical computation.** sympy is for derivation, numpy/scipy for computation.

## References
- SymPy: https://www.sympy.org/
