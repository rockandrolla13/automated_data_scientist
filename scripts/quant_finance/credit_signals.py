"""credit_signals — Credit-specific trading signals: momentum, carry, value, quality."""

import numpy as np
import pandas as pd


def spread_momentum(spreads: pd.Series, lookback: int = 20) -> pd.Series:
    """Spread momentum: change in spread over lookback.
    Negative = spreads tightened = bullish signal (return positive value for long signal).
    """
    return (-spreads.diff(lookback)).rename("spread_momentum")


def carry_signal(spreads: pd.Series, funding_rate: pd.Series | float = 0.0) -> pd.Series:
    """Carry: spread earned minus funding cost. Higher = more attractive."""
    if isinstance(funding_rate, (int, float)):
        carry = spreads - funding_rate
    else:
        carry = spreads - funding_rate
    return carry.rename("carry")


def value_signal(
    spreads: pd.Series,
    fair_spread: pd.Series,
) -> pd.Series:
    """Value: deviation from fair spread. Positive = cheap (spread > fair)."""
    return (spreads - fair_spread).rename("value")


def quality_signal(
    leverage: pd.Series,
    interest_coverage: pd.Series,
    weights: dict | None = None,
) -> pd.Series:
    """Quality composite: low leverage + high coverage = high quality.
    Returns signal where higher = better quality.
    """
    if weights is None:
        weights = {"leverage": -0.5, "coverage": 0.5}

    # Z-score each
    z_lev = (leverage - leverage.rolling(252).mean()) / leverage.rolling(252).std()
    z_cov = (interest_coverage - interest_coverage.rolling(252).mean()) / interest_coverage.rolling(252).std()

    quality = weights["leverage"] * z_lev + weights["coverage"] * z_cov
    return quality.rename("quality")


def composite_credit_signal(
    signals: dict[str, pd.Series],
    weights: dict[str, float] | None = None,
) -> pd.Series:
    """Combine credit signals via weighted z-score average."""
    df = pd.DataFrame(signals)
    if weights is None:
        weights = {k: 1.0 / len(signals) for k in signals}

    z = df.apply(lambda s: (s - s.rolling(60).mean()) / s.rolling(60).std())
    combined = sum(z[k].fillna(0) * w for k, w in weights.items())
    return combined.rename("composite_credit")


def signal_ic_report(
    signals: dict[str, pd.Series],
    forward_returns: pd.Series,
    lag: int = 1,
) -> pd.DataFrame:
    """IC (rank correlation) for each signal vs forward returns."""
    from scipy import stats

    rows = []
    for name, signal in signals.items():
        aligned = pd.DataFrame({"sig": signal.shift(lag), "ret": forward_returns}).dropna()
        if len(aligned) < 30:
            rows.append({"signal": name, "ic": np.nan, "ic_t": np.nan, "n": len(aligned)})
            continue
        ic, p = stats.spearmanr(aligned["sig"], aligned["ret"])
        ic_t = ic * np.sqrt(len(aligned)) / np.sqrt(1 - ic**2) if abs(ic) < 1 else np.nan
        rows.append({"signal": name, "ic": ic, "ic_t": ic_t, "n": len(aligned)})

    return pd.DataFrame(rows).sort_values("ic", ascending=False, key=abs)


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    idx = pd.date_range("2020-01-01", periods=500, freq="B")
    spreads = pd.Series(100 + np.cumsum(rng.normal(0, 1, 500)), index=idx)
    returns = pd.Series(rng.normal(0, 0.01, 500), index=idx)

    mom = spread_momentum(spreads, lookback=20)
    carry = carry_signal(spreads, funding_rate=50)
    fair = spreads.rolling(60).mean()
    val = value_signal(spreads, fair)

    combined = composite_credit_signal({"mom": mom, "carry": carry, "value": val})
    report = signal_ic_report({"mom": mom, "carry": carry, "value": val, "combined": combined}, returns)
    print(report.to_string(index=False))
