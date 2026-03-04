"""symbolic_math — Symbolic computation via SymPy for derivations and verification."""

import sympy as sp
from sympy import symbols, diff, integrate, simplify, solve, exp, sqrt, log, Rational


def derive_greeks(
    option_formula: sp.Expr,
    underlying: sp.Symbol,
    params: dict[str, sp.Symbol],
) -> dict[str, sp.Expr]:
    """Compute option Greeks symbolically."""
    S = underlying
    greeks = {
        "delta": simplify(diff(option_formula, S)),
        "gamma": simplify(diff(option_formula, S, 2)),
    }
    if "sigma" in params:
        greeks["vega"] = simplify(diff(option_formula, params["sigma"]))
    if "T" in params:
        greeks["theta"] = simplify(-diff(option_formula, params["T"]))
    if "r" in params:
        greeks["rho"] = simplify(diff(option_formula, params["r"]))
    return greeks


def solve_equation(expr: sp.Expr, variable: sp.Symbol) -> list:
    """Solve expr = 0 for variable."""
    return solve(expr, variable)


def latex_display(expr: sp.Expr) -> str:
    """Convert expression to LaTeX string."""
    return sp.latex(expr)


def verify_numerical(
    symbolic_expr: sp.Expr,
    var_values: dict,
    expected: float,
    tol: float = 1e-6,
) -> bool:
    """Check symbolic expression against numerical value."""
    result = float(symbolic_expr.evalf(subs=var_values))
    return abs(result - expected) < tol


def black_scholes_symbolic():
    """Return symbolic Black-Scholes call price formula."""
    from sympy.stats import Normal as SymNormal, cdf

    S, K, r, T, sigma = symbols("S K r T sigma", positive=True)
    d1 = (log(S / K) + (r + sigma**2 / 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    # Using sympy's Normal CDF
    N = sp.Function("N")  # placeholder for cumulative normal
    call = S * N(d1) - K * exp(-r * T) * N(d2)

    return call, {"S": S, "K": K, "r": r, "T": T, "sigma": sigma, "d1": d1, "d2": d2}


if __name__ == "__main__":
    S, K, r, T, sigma = symbols("S K r T sigma", positive=True)
    d1 = (log(S / K) + (r + sigma**2 / 2) * T) / (sigma * sqrt(T))
    delta = simplify(diff(d1, S))
    print(f"d(d1)/dS = {delta}")
    print(f"LaTeX: {latex_display(delta)}")
