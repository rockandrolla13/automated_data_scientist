"""arima — ARIMA/SARIMAX fitting, auto-order selection, Granger causality."""

from dataclasses import dataclass
import pandas as pd
import numpy as np


@dataclass
class ARIMAResult:
    order: tuple
    seasonal_order: tuple | None
    params: dict[str, float]
    aic: float
    bic: float
    residuals: pd.Series
    forecast: pd.Series | None
    ljung_box_pvalue: float


def fit_arima(
    series: pd.Series,
    order: tuple = (1, 0, 1),
    seasonal_order: tuple | None = None,
    exog: pd.DataFrame | None = None,
    forecast_steps: int = 0,
) -> ARIMAResult:
    """Fit ARIMA or SARIMAX."""
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    from statsmodels.stats.diagnostic import acorr_ljungbox

    s = series.dropna()
    model = SARIMAX(s, order=order, seasonal_order=seasonal_order or (0, 0, 0, 0),
                    exog=exog, enforce_stationarity=False, enforce_invertibility=False)
    res = model.fit(disp=False)

    lb = acorr_ljungbox(res.resid.dropna(), lags=[10], return_df=True)
    lb_p = lb["lb_pvalue"].iloc[0]

    fc = None
    if forecast_steps > 0:
        fc = res.forecast(steps=forecast_steps)

    return ARIMAResult(
        order=order,
        seasonal_order=seasonal_order,
        params=dict(res.params),
        aic=res.aic,
        bic=res.bic,
        residuals=res.resid,
        forecast=fc,
        ljung_box_pvalue=lb_p,
    )


def auto_select_order(
    series: pd.Series,
    max_p: int = 5,
    max_q: int = 5,
    max_d: int = 2,
    seasonal: bool = False,
    m: int = 1,
) -> tuple:
    """Auto-select ARIMA order via pmdarima."""
    import pmdarima as pm

    model = pm.auto_arima(
        series.dropna(), max_p=max_p, max_q=max_q, max_d=max_d,
        seasonal=seasonal, m=m, stepwise=True, suppress_warnings=True,
        error_action="ignore",
    )
    return model.order


def granger_causality(
    df: pd.DataFrame,
    target: str,
    cause: str,
    maxlag: int = 5,
) -> pd.DataFrame:
    """Granger causality test. Returns p-values per lag."""
    from statsmodels.tsa.stattools import grangercausalitytests

    data = df[[target, cause]].dropna()
    results = grangercausalitytests(data, maxlag=maxlag, verbose=False)

    rows = []
    for lag, res in results.items():
        f_test = res[0]["ssr_ftest"]
        rows.append({"lag": lag, "f_stat": f_test[0], "p_value": f_test[1]})

    return pd.DataFrame(rows)


if __name__ == "__main__":
    import json

    CONFIG = {
        "data_source": "../../data/returns_clean.parquet",
        "column": "returns",
        "auto_order": True,
    }

    df = pd.read_parquet(CONFIG["data_source"])
    s = df[CONFIG["column"]]

    if CONFIG["auto_order"]:
        order = auto_select_order(s)
        print(f"Auto-selected order: {order}")
    else:
        order = (1, 0, 1)

    result = fit_arima(s, order=order, forecast_steps=10)
    print(f"AIC: {result.aic:.1f}, Ljung-Box p: {result.ljung_box_pvalue:.4f}")

    with open("results.json", "w") as f:
        json.dump({"order": list(result.order), "aic": result.aic,
                    "ljung_box_p": result.ljung_box_pvalue}, f, indent=2)
