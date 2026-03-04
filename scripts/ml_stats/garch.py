"""garch — GARCH-family volatility models via arch package."""

from dataclasses import dataclass
import pandas as pd
import numpy as np


@dataclass
class GARCHResult:
    params: dict[str, float]
    conditional_vol: pd.Series
    persistence: float
    aic: float
    bic: float
    loglikelihood: float
    vol_forecast: np.ndarray | None
    model_type: str
    distribution: str
    converged: bool


def fit_garch(
    returns: pd.Series,
    p: int = 1,
    q: int = 1,
    model_type: str = "GARCH",
    dist: str = "t",
    mean: str = "Zero",
    rescale: bool = True,
) -> GARCHResult:
    """Fit GARCH-family model. Returns typed result.

    Args:
        returns: Return series. If decimal, auto-rescaled to percentage.
        model_type: GARCH, EGARCH, GJR-GARCH, TGARCH
        dist: normal, t, skewt, ged
        mean: Zero, Constant, AR
        rescale: If True and |mean| < 0.05, multiply by 100 for arch.
    """
    from arch import arch_model

    r = returns.dropna().copy()
    if rescale and r.abs().mean() < 0.05:
        r = r * 100

    vol_model = model_type.replace("-", "")
    am = arch_model(r, mean=mean, vol=vol_model, p=p, q=q, dist=dist)

    try:
        res = am.fit(disp="off", show_warning=False)
        converged = True
    except Exception:
        res = am.fit(disp="off", show_warning=False, options={"maxiter": 500})
        converged = res.convergence_flag == 0

    params = dict(res.params)
    cond_vol = res.conditional_volatility
    if rescale and returns.abs().mean() < 0.05:
        cond_vol = cond_vol / 100

    persistence = sum(v for k, v in params.items() if k.startswith(("alpha", "beta", "gamma")))

    return GARCHResult(
        params=params,
        conditional_vol=cond_vol,
        persistence=persistence,
        aic=res.aic,
        bic=res.bic,
        loglikelihood=res.loglikelihood,
        vol_forecast=None,
        model_type=model_type,
        distribution=dist,
        converged=converged,
    )


def forecast_vol(
    returns: pd.Series,
    result: GARCHResult,
    horizon: int = 10,
    p: int = 1,
    q: int = 1,
) -> pd.DataFrame:
    """Generate h-step ahead vol forecast."""
    from arch import arch_model

    r = returns.dropna().copy()
    if r.abs().mean() < 0.05:
        r = r * 100

    am = arch_model(r, mean="Zero", vol=result.model_type.replace("-", ""),
                     p=p, q=q, dist=result.distribution)
    res = am.fit(disp="off", show_warning=False)
    fc = res.forecast(horizon=horizon)

    return pd.DataFrame({
        "variance": fc.variance.iloc[-1].values,
        "vol": np.sqrt(fc.variance.iloc[-1].values),
    }, index=range(1, horizon + 1))


def compare_models(
    returns: pd.Series,
    models: list[dict] | None = None,
) -> pd.DataFrame:
    """Compare multiple GARCH specs. Returns AIC/BIC table."""
    if models is None:
        models = [
            {"model_type": "GARCH", "p": 1, "q": 1},
            {"model_type": "EGARCH", "p": 1, "q": 1},
            {"model_type": "GJR-GARCH", "p": 1, "q": 1},
            {"model_type": "GARCH", "p": 2, "q": 1},
        ]

    rows = []
    for spec in models:
        label = f"{spec['model_type']}({spec['p']},{spec['q']})"
        try:
            res = fit_garch(returns, **spec)
            rows.append({
                "model": label, "aic": res.aic, "bic": res.bic,
                "persistence": res.persistence, "converged": res.converged,
            })
        except Exception as e:
            rows.append({"model": label, "aic": np.nan, "bic": np.nan,
                         "persistence": np.nan, "converged": False})

    df = pd.DataFrame(rows).sort_values("bic")
    return df


if __name__ == "__main__":
    import json

    CONFIG = {
        "data_source": "../../data/returns_clean.parquet",
        "column": "returns",
        "p": 1, "q": 1,
        "model_type": "GARCH",
        "dist": "t",
    }

    df = pd.read_parquet(CONFIG["data_source"])
    result = fit_garch(df[CONFIG["column"]], p=CONFIG["p"], q=CONFIG["q"],
                       model_type=CONFIG["model_type"], dist=CONFIG["dist"])

    print(f"Params: {result.params}")
    print(f"Persistence: {result.persistence:.4f}")
    print(f"AIC: {result.aic:.1f}, BIC: {result.bic:.1f}")

    output = {
        "params": {k: round(v, 6) for k, v in result.params.items()},
        "persistence": round(result.persistence, 4),
        "aic": round(result.aic, 1),
        "bic": round(result.bic, 1),
        "converged": result.converged,
    }
    with open("results.json", "w") as f:
        json.dump(output, f, indent=2)
