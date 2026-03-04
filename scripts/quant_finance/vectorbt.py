"""vectorbt — High-performance vectorized backtesting and parameter sweeps."""

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class VBTResult:
    total_return: float
    sharpe: float
    max_drawdown: float
    n_trades: int
    win_rate: float
    stats: dict


def run_vbt_backtest(
    close: pd.Series,
    entries: pd.Series,
    exits: pd.Series,
    fees: float = 0.0005,
    freq: str = "1D",
    direction: str = "longonly",
) -> VBTResult:
    """Run vectorbt backtest from boolean entry/exit signals."""
    import vectorbt as vbt

    pf = vbt.Portfolio.from_signals(
        close, entries=entries, exits=exits,
        fees=fees, freq=freq, direction=direction,
    )

    stats = pf.stats().to_dict()
    trades = pf.trades.records_readable

    return VBTResult(
        total_return=pf.total_return(),
        sharpe=pf.sharpe_ratio(),
        max_drawdown=pf.max_drawdown(),
        n_trades=len(trades) if trades is not None else 0,
        win_rate=pf.trades.win_rate() if len(trades) > 0 else 0,
        stats=stats,
    )


def parameter_sweep(
    close: pd.Series,
    fast_range: range = range(5, 30, 5),
    slow_range: range = range(20, 100, 10),
    fees: float = 0.0005,
) -> pd.DataFrame:
    """SMA crossover parameter sweep."""
    import vectorbt as vbt

    fast_ma, slow_ma = vbt.MA.run_combs(close, window=list(fast_range), r=2, short_names=["fast", "slow"])
    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)

    pf = vbt.Portfolio.from_signals(close, entries=entries, exits=exits, fees=fees)

    results = pd.DataFrame({
        "total_return": pf.total_return(),
        "sharpe": pf.sharpe_ratio(),
        "max_drawdown": pf.max_drawdown(),
        "n_trades": pf.trades.count(),
    })

    return results.sort_values("sharpe", ascending=False)


def plot_vbt_results(close: pd.Series, entries: pd.Series, exits: pd.Series,
                     fees: float = 0.0005, path: str | None = None):
    """Generate equity curve and drawdown plot."""
    import vectorbt as vbt

    pf = vbt.Portfolio.from_signals(close, entries=entries, exits=exits, fees=fees)

    if path:
        fig = pf.plot()
        fig.write_html(path)
    return pf


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    idx = pd.date_range("2020-01-01", periods=500, freq="B")
    close = pd.Series(100 * np.cumprod(1 + rng.normal(0.0003, 0.01, 500)), index=idx)

    # Simple SMA crossover
    fast = close.rolling(10).mean()
    slow = close.rolling(50).mean()
    entries = (fast > slow) & (fast.shift(1) <= slow.shift(1))
    exits = (fast < slow) & (fast.shift(1) >= slow.shift(1))

    print("vectorbt requires: pip install vectorbt")
    print(f"Generated {entries.sum()} entries, {exits.sum()} exits")
