"""large_scale_processing — Dask and Polars for out-of-core computation."""

import pandas as pd
import numpy as np
from pathlib import Path


def load_lazy_dask(path: str):
    """Lazy-load with Dask. Returns dask DataFrame."""
    import dask.dataframe as dd
    p = Path(path)
    if p.suffix == ".parquet":
        return dd.read_parquet(path)
    elif p.suffix == ".csv":
        return dd.read_csv(path)
    raise ValueError(f"Unsupported: {p.suffix}")


def load_lazy_polars(path: str):
    """Lazy-load with Polars. Returns LazyFrame."""
    import polars as pl
    p = Path(path)
    if p.suffix == ".parquet":
        return pl.scan_parquet(path)
    elif p.suffix == ".csv":
        return pl.scan_csv(path)
    raise ValueError(f"Unsupported: {p.suffix}")


def rolling_stats_dask(ddf, col: str, window: int) -> pd.DataFrame:
    """Parallel rolling mean and std via Dask. Returns pandas DataFrame."""
    import dask.dataframe as dd
    result = ddf.assign(
        rolling_mean=ddf[col].rolling(window).mean(),
        rolling_std=ddf[col].rolling(window).std(),
    )
    return result.compute()


def downsample_polars(path: str, date_col: str, freq: str = "1d", agg: str = "mean"):
    """Downsample large dataset via Polars group_by_dynamic."""
    import polars as pl
    lf = pl.scan_parquet(path)
    result = (
        lf.sort(date_col)
        .group_by_dynamic(date_col, every=freq)
        .agg(pl.all().exclude(date_col).mean() if agg == "mean" else pl.all().exclude(date_col).last())
    )
    return result.collect()


if __name__ == "__main__":
    CONFIG = {
        "data_source": "../../data/large_dataset.parquet",
        "engine": "polars",
    }

    if CONFIG["engine"] == "polars":
        lf = load_lazy_polars(CONFIG["data_source"])
        print(lf.describe_plan())
    else:
        ddf = load_lazy_dask(CONFIG["data_source"])
        print(f"Partitions: {ddf.npartitions}")
