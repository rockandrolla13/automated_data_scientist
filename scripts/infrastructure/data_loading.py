"""data_loading — File loading, API fetching, and column standardization."""

from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import numpy as np


def load_file(path: str, index_col: int | str = 0, parse_dates: bool = True) -> pd.DataFrame:
    """Auto-detect format and load. Returns DataFrame with DatetimeIndex if possible."""
    p = Path(path)
    ext = p.suffix.lower()

    if ext == ".parquet":
        df = pd.read_parquet(path)
    elif ext == ".csv":
        df = pd.read_csv(path, index_col=index_col, parse_dates=parse_dates)
    elif ext in (".xls", ".xlsx"):
        df = pd.read_excel(path, index_col=index_col, parse_dates=parse_dates)
    elif ext == ".json":
        df = pd.read_json(path)
    else:
        raise ValueError(f"Unsupported format: {ext}")

    # Strip timezone if present
    if isinstance(df.index, pd.DatetimeIndex) and df.index.tz is not None:
        df.index = df.index.tz_localize(None)

    return df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase, replace spaces with underscores, strip whitespace."""
    out = df.copy()
    out.columns = (
        out.columns
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w]", "_", regex=True)
        .str.replace(r"_+", "_", regex=True)
        .str.strip("_")
    )
    return out


def load_fred(
    series_ids: list[str],
    start: str = "2000-01-01",
    end: str | None = None,
    api_key: str | None = None,
) -> pd.DataFrame:
    """Fetch series from FRED. Requires FRED_API_KEY env var or api_key param."""
    import os
    try:
        from fredapi import Fred
    except ImportError:
        raise ImportError("pip install fredapi")

    key = api_key or os.environ.get("FRED_API_KEY")
    if not key:
        raise ValueError("Set FRED_API_KEY env var or pass api_key")

    fred = Fred(api_key=key)
    frames = {}
    for sid in series_ids:
        frames[sid] = fred.get_series(sid, observation_start=start, observation_end=end)

    return pd.DataFrame(frames)


def save_parquet(df: pd.DataFrame, path: str) -> None:
    """Save DataFrame as Parquet. Always use this for intermediate data."""
    df.to_parquet(path)


if __name__ == "__main__":
    import sys

    CONFIG = {
        "data_source": "../../data/raw.csv",
        "output": "../../data/raw_loaded.parquet",
    }

    df = load_file(CONFIG["data_source"])
    df = standardize_columns(df)
    print(f"Loaded: {df.shape}, columns: {list(df.columns)}")
    save_parquet(df, CONFIG["output"])
    print(f"Saved: {CONFIG['output']}")
