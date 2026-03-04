"""EDA — Exploratory data analysis with stationarity, outlier, and profiling functions."""

from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from scipy import stats


@dataclass
class StationarityResult:
    adf_stat: float
    adf_pvalue: float
    kpss_stat: float
    kpss_pvalue: float
    is_stationary: bool
    recommendation: str


@dataclass
class OutlierResult:
    n_outliers: int
    outlier_indices: list
    method: str
    threshold: float
    pct_outliers: float


@dataclass
class EDAReport:
    shape: tuple
    dtypes: dict
    null_counts: dict
    null_pcts: dict
    numeric_stats: dict  # col -> {mean, std, min, max, skew, kurt}
    duplicate_rows: int
    duplicate_timestamps: int
    stationarity: dict  # col -> StationarityResult (numeric cols only)
    outliers: dict  # col -> OutlierResult
    warnings: list[str] = field(default_factory=list)


def check_stationarity(series: pd.Series, significance: float = 0.05) -> StationarityResult:
    """ADF + KPSS joint test. Returns recommendation."""
    from statsmodels.tsa.stattools import adfuller, kpss

    clean = series.dropna()
    if len(clean) < 30:
        return StationarityResult(
            adf_stat=np.nan, adf_pvalue=np.nan,
            kpss_stat=np.nan, kpss_pvalue=np.nan,
            is_stationary=False, recommendation="n < 30, cannot test"
        )

    adf = adfuller(clean, autolag="AIC")
    adf_stat, adf_p = adf[0], adf[1]

    kpss_res = kpss(clean, regression="c", nlags="auto")
    kpss_stat, kpss_p = kpss_res[0], kpss_res[1]

    adf_reject = adf_p < significance  # reject unit root → stationary
    kpss_reject = kpss_p < significance  # reject stationary → non-stationary

    if adf_reject and not kpss_reject:
        rec = "stationary"
        is_stat = True
    elif not adf_reject and kpss_reject:
        rec = "non-stationary — difference the series"
        is_stat = False
    elif adf_reject and kpss_reject:
        rec = "trend-stationary — detrend or difference"
        is_stat = False
    else:
        rec = "ambiguous — inspect ACF/PACF manually"
        is_stat = False

    return StationarityResult(
        adf_stat=adf_stat, adf_pvalue=adf_p,
        kpss_stat=kpss_stat, kpss_pvalue=kpss_p,
        is_stationary=is_stat, recommendation=rec,
    )


def detect_outliers(
    series: pd.Series,
    method: str = "iqr",
    threshold: float = 3.0,
) -> OutlierResult:
    """Detect outliers via IQR, z-score, or MAD."""
    clean = series.dropna()

    if method == "iqr":
        q1, q3 = clean.quantile(0.25), clean.quantile(0.75)
        iqr = q3 - q1
        mask = (clean < q1 - threshold * iqr) | (clean > q3 + threshold * iqr)
    elif method == "zscore":
        z = np.abs(stats.zscore(clean))
        mask = z > threshold
    elif method == "mad":
        med = clean.median()
        mad = np.median(np.abs(clean - med))
        if mad == 0:
            mask = pd.Series(False, index=clean.index)
        else:
            modified_z = 0.6745 * (clean - med) / mad
            mask = np.abs(modified_z) > threshold
    else:
        raise ValueError(f"Unknown method: {method}. Use 'iqr', 'zscore', or 'mad'.")

    idx = clean[mask].index.tolist()
    return OutlierResult(
        n_outliers=len(idx),
        outlier_indices=idx,
        method=method,
        threshold=threshold,
        pct_outliers=len(idx) / len(clean) * 100 if len(clean) > 0 else 0,
    )


def profile_dataframe(
    df: pd.DataFrame,
    outlier_method: str = "iqr",
    check_stationarity_cols: bool = True,
) -> EDAReport:
    """Full EDA profile. Returns structured report."""
    warnings = []

    # Basic shape
    null_counts = df.isnull().sum().to_dict()
    null_pcts = (df.isnull().sum() / len(df) * 100).to_dict()

    # Flag high-null columns
    for col, pct in null_pcts.items():
        if pct > 5:
            warnings.append(f"{col}: {pct:.1f}% null")

    # Numeric stats
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    numeric_stats = {}
    for col in numeric_cols:
        s = df[col].dropna()
        numeric_stats[col] = {
            "mean": s.mean(), "std": s.std(), "min": s.min(), "max": s.max(),
            "skew": s.skew(), "kurtosis": s.kurtosis(),
            "q01": s.quantile(0.01), "q99": s.quantile(0.99),
        }
        if abs(s.skew()) > 2:
            warnings.append(f"{col}: high skewness ({s.skew():.2f})")
        if s.kurtosis() > 6:
            warnings.append(f"{col}: high kurtosis ({s.kurtosis():.2f})")

    # Duplicates
    dup_rows = df.duplicated().sum()
    dup_ts = 0
    if isinstance(df.index, pd.DatetimeIndex):
        dup_ts = df.index.duplicated().sum()
        if dup_ts > 0:
            warnings.append(f"{dup_ts} duplicate timestamps")

    # Stationarity (numeric, time-indexed)
    stationarity = {}
    if check_stationarity_cols and isinstance(df.index, pd.DatetimeIndex):
        for col in numeric_cols:
            stationarity[col] = check_stationarity(df[col])

    # Outliers
    outliers = {}
    for col in numeric_cols:
        outliers[col] = detect_outliers(df[col], method=outlier_method)

    return EDAReport(
        shape=df.shape,
        dtypes={str(k): str(v) for k, v in df.dtypes.to_dict().items()},
        null_counts=null_counts,
        null_pcts=null_pcts,
        numeric_stats=numeric_stats,
        duplicate_rows=dup_rows,
        duplicate_timestamps=dup_ts,
        stationarity=stationarity,
        outliers=outliers,
        warnings=warnings,
    )


def clean_dataframe(
    df: pd.DataFrame,
    report: EDAReport,
    ffill_prices: bool = True,
    drop_duplicate_timestamps: bool = True,
) -> pd.DataFrame:
    """Apply standard cleaning based on EDA report. Returns clean copy."""
    out = df.copy()

    # Deduplicate timestamps
    if drop_duplicate_timestamps and isinstance(out.index, pd.DatetimeIndex):
        out = out[~out.index.duplicated(keep="last")]

    # Forward-fill numeric columns (price-like)
    if ffill_prices:
        numeric_cols = out.select_dtypes(include=[np.number]).columns
        out[numeric_cols] = out[numeric_cols].ffill()

    return out


if __name__ == "__main__":
    import json
    import sys

    CONFIG = {
        "data_source": "../../data/raw.parquet",
        "outlier_method": "iqr",
        "output_clean": "../../data/raw_clean.parquet",
    }

    path = CONFIG["data_source"]
    if path.endswith(".csv"):
        df = pd.read_csv(path, parse_dates=True, index_col=0)
    else:
        df = pd.read_parquet(path)

    report = profile_dataframe(df, outlier_method=CONFIG["outlier_method"])

    print(f"Shape: {report.shape}")
    print(f"Warnings: {report.warnings}")
    for col, sr in report.stationarity.items():
        print(f"  {col}: {sr.recommendation}")

    clean = clean_dataframe(df, report)
    clean.to_parquet(CONFIG["output_clean"])
    print(f"Clean data saved: {CONFIG['output_clean']}")

    results = {
        "shape": list(report.shape),
        "null_pcts": report.null_pcts,
        "warnings": report.warnings,
        "stationarity": {k: v.recommendation for k, v in report.stationarity.items()},
        "outlier_counts": {k: v.n_outliers for k, v in report.outliers.items()},
    }
    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)
