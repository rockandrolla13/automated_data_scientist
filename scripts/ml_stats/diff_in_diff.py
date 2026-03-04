"""diff_in_diff — Difference-in-differences estimation."""

from dataclasses import dataclass
import pandas as pd
import numpy as np


@dataclass
class DIDResult:
    delta: float
    se: float
    t_stat: float
    p_value: float
    ci_lower: float
    ci_upper: float
    n_obs: int
    r_squared: float


def fit_did(
    df: pd.DataFrame,
    outcome: str,
    treat_col: str,
    post_col: str,
    controls: list[str] | None = None,
    cluster_col: str | None = None,
) -> DIDResult:
    """Basic 2x2 DiD via OLS."""
    import statsmodels.formula.api as smf

    formula = f"{outcome} ~ {treat_col} * {post_col}"
    if controls:
        formula += " + " + " + ".join(controls)

    cov_kwds = {}
    if cluster_col:
        cov_kwds = {"cov_type": "cluster", "cov_kwds": {"groups": df[cluster_col]}}

    model = smf.ols(formula, data=df).fit(**cov_kwds)

    interaction = f"{treat_col}:{post_col}"
    delta = model.params[interaction]
    se = model.bse[interaction]
    t = model.tvalues[interaction]
    p = model.pvalues[interaction]
    ci = model.conf_int().loc[interaction]

    return DIDResult(
        delta=delta, se=se, t_stat=t, p_value=p,
        ci_lower=ci[0], ci_upper=ci[1],
        n_obs=int(model.nobs), r_squared=model.rsquared,
    )


def event_study(
    df: pd.DataFrame,
    outcome: str,
    treat_col: str,
    time_col: str,
    event_time: int = 0,
    n_pre: int = 4,
    n_post: int = 4,
) -> pd.DataFrame:
    """Event study with leads and lags. Returns coefficient table."""
    import statsmodels.formula.api as smf

    df = df.copy()
    df["rel_time"] = df[time_col] - event_time

    dummies = []
    for t in range(-n_pre, n_post + 1):
        if t == -1:
            continue  # reference period
        col = f"rel_{t}" if t >= 0 else f"rel_m{abs(t)}"
        df[col] = ((df["rel_time"] == t) & (df[treat_col] == 1)).astype(int)
        dummies.append(col)

    formula = f"{outcome} ~ " + " + ".join(dummies)
    model = smf.ols(formula, data=df).fit()

    rows = []
    for t, col in zip([t for t in range(-n_pre, n_post + 1) if t != -1], dummies):
        rows.append({
            "relative_time": t,
            "coefficient": model.params[col],
            "se": model.bse[col],
            "p_value": model.pvalues[col],
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    n = 1000
    df = pd.DataFrame({
        "treat": np.repeat([0, 1], n // 2),
        "post": np.tile([0, 1], n // 2),
        "y": rng.normal(size=n),
    })
    df.loc[(df.treat == 1) & (df.post == 1), "y"] += 0.5
    result = fit_did(df, "y", "treat", "post")
    print(f"DiD estimate: {result.delta:.3f} (p={result.p_value:.4f})")
