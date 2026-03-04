"""spread_decomposition — Decompose credit spreads into default, liquidity, residual."""

from dataclasses import dataclass
import numpy as np
import pandas as pd
import statsmodels.api as sm


@dataclass
class DecompResult:
    coefficients: dict[str, float]
    r_squared: float
    default_component: pd.Series
    liquidity_component: pd.Series
    residual: pd.Series
    vif: dict[str, float] | None


def decompose_spread(
    spreads: pd.Series,
    default_proxy: pd.Series,
    liquidity_proxy: pd.Series,
    macro: pd.Series | pd.DataFrame | None = None,
    add_constant: bool = True,
) -> DecompResult:
    """Regress spreads on default, liquidity, and macro factors."""
    from statsmodels.stats.outliers_influence import variance_inflation_factor

    df = pd.DataFrame({
        "spread": spreads,
        "default": default_proxy,
        "liquidity": liquidity_proxy,
    }).dropna()

    X_cols = ["default", "liquidity"]
    if macro is not None:
        if isinstance(macro, pd.Series):
            df["macro"] = macro
            X_cols.append("macro")
        else:
            for col in macro.columns:
                df[col] = macro[col]
                X_cols.append(col)

    df = df.dropna()
    X = df[X_cols]
    if add_constant:
        X = sm.add_constant(X)
    y = df["spread"]

    model = sm.OLS(y, X).fit()

    # VIF
    vif = None
    if len(X_cols) >= 2:
        X_vif = df[X_cols]
        vif = {X_cols[i]: variance_inflation_factor(X_vif.values, i) for i in range(len(X_cols))}

    # Components
    default_comp = model.params.get("default", 0) * df["default"]
    liq_comp = model.params.get("liquidity", 0) * df["liquidity"]
    resid = model.resid

    return DecompResult(
        coefficients=dict(model.params),
        r_squared=model.rsquared,
        default_component=default_comp,
        liquidity_component=liq_comp,
        residual=resid,
        vif=vif,
    )


def compute_basis(cds_spread: pd.Series, bond_spread: pd.Series) -> pd.Series:
    """CDS-bond basis in bps. Positive = bond is cheap relative to CDS."""
    return (cds_spread - bond_spread).rename("basis_bps")


def regime_decomposition(
    spreads: pd.Series,
    default_proxy: pd.Series,
    liquidity_proxy: pd.Series,
    regimes: pd.Series,
) -> pd.DataFrame:
    """Run decomposition within each regime."""
    rows = []
    for regime in sorted(regimes.unique()):
        mask = regimes == regime
        try:
            result = decompose_spread(
                spreads[mask], default_proxy[mask], liquidity_proxy[mask],
            )
            rows.append({
                "regime": regime, "n": mask.sum(), "r2": result.r_squared,
                "beta_default": result.coefficients.get("default", np.nan),
                "beta_liquidity": result.coefficients.get("liquidity", np.nan),
            })
        except Exception:
            rows.append({"regime": regime, "n": mask.sum(), "r2": np.nan,
                         "beta_default": np.nan, "beta_liquidity": np.nan})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    n = 500
    default = rng.normal(100, 20, n)
    liquidity = rng.exponential(10, n)
    spreads = 0.6 * default + 0.3 * liquidity + rng.normal(0, 5, n)

    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    result = decompose_spread(
        pd.Series(spreads, index=idx), pd.Series(default, index=idx),
        pd.Series(liquidity, index=idx),
    )
    print(f"R²: {result.r_squared:.3f}")
    print(f"Coefficients: {result.coefficients}")
    print(f"VIF: {result.vif}")
