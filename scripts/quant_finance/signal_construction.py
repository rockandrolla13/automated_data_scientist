"""signal_construction — Trading signal building blocks: momentum, mean-reversion, z-score, combination."""

import numpy as np
import pandas as pd
from scipy import stats


def momentum_signal(prices: pd.Series, lookback: int = 20) -> pd.Series:
    """Price momentum: return over lookback period."""
    return prices.pct_change(lookback).rename("momentum")


def mean_reversion_signal(
    series: pd.Series,
    window: int = 20,
    z_threshold: float = 0.0,
) -> pd.Series:
    """Mean-reversion: negative z-score (high → sell, low → buy)."""
    z = zscore_normalize(series, window)
    return (-z).rename("mean_reversion")


def zscore_normalize(signal: pd.Series, window: int = 60) -> pd.Series:
    """Rolling z-score normalization."""
    mu = signal.rolling(window).mean()
    sigma = signal.rolling(window).std()
    return ((signal - mu) / sigma.replace(0, np.nan)).rename(f"{signal.name}_z")


def rank_signal(signal: pd.DataFrame) -> pd.DataFrame:
    """Cross-sectional percentile rank (0 to 1) per row."""
    return signal.rank(axis=1, pct=True)


def combine_signals(
    signals: dict[str, pd.Series],
    weights: dict[str, float] | None = None,
    method: str = "weighted",
) -> pd.Series:
    """Combine multiple signals.

    Methods:
        weighted: weighted sum of z-scored signals
        rank: average cross-sectional rank
        vote: sign agreement (majority vote)
    """
    df = pd.DataFrame(signals)

    if method == "weighted":
        if weights is None:
            weights = {k: 1.0 / len(signals) for k in signals}
        # Z-score each signal first
        z = df.apply(lambda s: (s - s.rolling(60).mean()) / s.rolling(60).std())
        combined = sum(z[k] * weights[k] for k in weights)
    elif method == "rank":
        ranked = df.rank(pct=True)
        combined = ranked.mean(axis=1)
    elif method == "vote":
        combined = np.sign(df).mean(axis=1)
    else:
        raise ValueError(f"Unknown method: {method}")

    return combined.rename("combined_signal")


def information_coefficient(signal: pd.Series, forward_returns: pd.Series, lag: int = 1) -> float:
    """IC: rank correlation between signal and forward returns."""
    aligned = pd.DataFrame({"signal": signal.shift(lag), "ret": forward_returns}).dropna()
    ic, _ = stats.spearmanr(aligned["signal"], aligned["ret"])
    return ic


def ic_series(signal: pd.Series, forward_returns: pd.Series, window: int = 60) -> pd.Series:
    """Rolling IC over time."""
    aligned = pd.DataFrame({"signal": signal.shift(1), "ret": forward_returns}).dropna()
    ic = aligned.rolling(window).apply(
        lambda x: stats.spearmanr(x.iloc[:, 0], x.iloc[:, 1])[0] if len(x) > 10 else np.nan,
        raw=False,
    )
    # rolling on DataFrame doesn't work cleanly — use loop
    ics = []
    for i in range(window, len(aligned)):
        chunk = aligned.iloc[i - window:i]
        ic_val, _ = stats.spearmanr(chunk["signal"], chunk["ret"])
        ics.append(ic_val)
    return pd.Series(ics, index=aligned.index[window:], name="rolling_ic")


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    idx = pd.date_range("2020-01-01", periods=500, freq="B")
    prices = pd.Series(100 * np.cumprod(1 + rng.normal(0.0003, 0.01, 500)), index=idx)
    returns = prices.pct_change()

    mom = momentum_signal(prices, lookback=20)
    mr = mean_reversion_signal(prices, window=60)
    combined = combine_signals({"mom": mom, "mr": mr})

    ic = information_coefficient(combined, returns.shift(-1))
    print(f"Combined signal IC: {ic:.4f}")
