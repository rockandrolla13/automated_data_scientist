"""liquidity_scorer — Bond/asset liquidity metrics: Amihud, bid-ask proxy, composite score."""

import numpy as np
import pandas as pd


def amihud_illiquidity(
    returns: pd.Series,
    volume: pd.Series,
    window: int = 20,
) -> pd.Series:
    """Amihud (2002) illiquidity: mean(|r|/volume) over rolling window."""
    ratio = returns.abs() / volume.replace(0, np.nan)
    return ratio.rolling(window).mean().rename("amihud")


def bid_ask_spread_proxy(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
) -> pd.Series:
    """Corwin-Schultz (2012) bid-ask spread estimator from high/low prices."""
    log_hl = np.log(high / low) ** 2

    # 2-day high-low range
    high_2d = pd.concat([high, high.shift(1)], axis=1).max(axis=1)
    low_2d = pd.concat([low, low.shift(1)], axis=1).min(axis=1)
    log_hl_2d = np.log(high_2d / low_2d) ** 2

    beta = log_hl + log_hl.shift(1)
    gamma = log_hl_2d

    alpha = (np.sqrt(2 * beta) - np.sqrt(beta)) / (3 - 2 * np.sqrt(2)) - np.sqrt(gamma / (3 - 2 * np.sqrt(2)))
    spread = 2 * (np.exp(alpha) - 1) / (1 + np.exp(alpha))
    return spread.clip(lower=0).rename("cs_spread")


def turnover_ratio(volume: pd.Series, shares_outstanding: float, window: int = 20) -> pd.Series:
    """Rolling turnover ratio."""
    return (volume / shares_outstanding).rolling(window).mean().rename("turnover")


def composite_score(
    metrics: dict[str, pd.Series],
    weights: dict[str, float] | None = None,
    higher_is_more_liquid: dict[str, bool] | None = None,
) -> pd.Series:
    """Combine liquidity metrics into single score (higher = more liquid)."""
    if weights is None:
        weights = {k: 1.0 / len(metrics) for k in metrics}
    if higher_is_more_liquid is None:
        higher_is_more_liquid = {k: False for k in metrics}  # default: higher metric = less liquid

    df = pd.DataFrame(metrics)
    # Z-score normalize
    z = (df - df.rolling(252).mean()) / df.rolling(252).std()

    score = pd.Series(0, index=df.index, dtype=float)
    for name, w in weights.items():
        direction = 1 if higher_is_more_liquid.get(name, False) else -1
        score += direction * z[name].fillna(0) * w

    return score.rename("liquidity_score")


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    idx = pd.date_range("2020-01-01", periods=500, freq="B")
    returns = pd.Series(rng.normal(0, 0.01, 500), index=idx)
    volume = pd.Series(rng.lognormal(15, 1, 500), index=idx)

    amihud = amihud_illiquidity(returns, volume)
    print(f"Amihud mean: {amihud.mean():.2e}")
