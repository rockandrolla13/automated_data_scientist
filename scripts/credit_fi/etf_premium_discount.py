"""etf_premium_discount — ETF premium/discount analysis for credit ETFs."""

from dataclasses import dataclass
import numpy as np
import pandas as pd


def compute_premium(price: pd.Series, nav: pd.Series) -> pd.Series:
    """(Price - NAV) / NAV in basis points."""
    return ((price - nav) / nav * 10000).rename("premium_bps")


def rolling_premium_stats(premium: pd.Series, window: int = 20) -> pd.DataFrame:
    """Rolling statistics of premium/discount."""
    return pd.DataFrame({
        "mean": premium.rolling(window).mean(),
        "std": premium.rolling(window).std(),
        "z_score": (premium - premium.rolling(window).mean()) / premium.rolling(window).std(),
        "percentile": premium.rolling(window).rank(pct=True),
    })


@dataclass
class StressEpisode:
    start: pd.Timestamp
    end: pd.Timestamp
    duration_days: int
    max_premium_bps: float
    min_premium_bps: float
    mean_premium_bps: float


def detect_stress_episodes(
    premium: pd.Series,
    threshold_bps: float = 50,
    min_duration: int = 2,
) -> list[StressEpisode]:
    """Identify periods where |premium| exceeds threshold."""
    stressed = premium.abs() > threshold_bps
    episodes = []
    in_episode = False
    start = None

    for date, is_stressed in stressed.items():
        if is_stressed and not in_episode:
            start = date
            in_episode = True
        elif not is_stressed and in_episode:
            end = date
            ep_data = premium[start:end]
            if len(ep_data) >= min_duration:
                episodes.append(StressEpisode(
                    start=start, end=end, duration_days=len(ep_data),
                    max_premium_bps=ep_data.max(), min_premium_bps=ep_data.min(),
                    mean_premium_bps=ep_data.mean(),
                ))
            in_episode = False

    return episodes


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    idx = pd.date_range("2020-01-01", periods=500, freq="B")
    nav = pd.Series(100 + np.cumsum(rng.normal(0, 0.1, 500)), index=idx)
    price = nav + rng.normal(0, 0.05, 500)
    price.iloc[200:210] += 0.8  # stress episode

    prem = compute_premium(price, nav)
    episodes = detect_stress_episodes(prem, threshold_bps=30)
    print(f"Premium mean: {prem.mean():.1f} bps, std: {prem.std():.1f} bps")
    print(f"Stress episodes: {len(episodes)}")
    for ep in episodes:
        print(f"  {ep.start.date()} to {ep.end.date()} ({ep.duration_days}d, max={ep.max_premium_bps:.0f}bps)")
