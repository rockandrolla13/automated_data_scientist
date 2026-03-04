"""backtest_engine — Signal-to-PnL backtesting with transaction costs and metrics."""

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class BacktestResult:
    returns: pd.Series
    cumulative: pd.Series
    sharpe: float
    t_stat: float
    max_drawdown: float
    information_ratio: float
    turnover: float
    total_costs: float
    n_trades: int


def backtest(
    signals: pd.Series,
    returns: pd.Series,
    costs_bps: float = 5.0,
    max_position: float = 1.0,
) -> BacktestResult:
    """Backtest: signal at t → position at t → return t to t+1.

    Args:
        signals: Position signal in [-1, 1]. Clipped to max_position.
        returns: Forward returns (decimal). Aligned: signal[t] earns returns[t+1].
        costs_bps: One-way transaction cost in bps.
    """
    common = signals.index.intersection(returns.index)
    sig = signals.loc[common].clip(-max_position, max_position)
    ret = returns.loc[common]

    # Shift signal: signal at t earns return at t+1
    pos = sig.shift(1).fillna(0)
    gross_ret = pos * ret

    # Transaction costs
    turnover = pos.diff().abs()
    cost_per_trade = costs_bps / 10000
    costs = turnover * cost_per_trade
    net_ret = gross_ret - costs

    # Metrics
    metrics = compute_metrics(net_ret)

    cum = (1 + net_ret).cumprod()
    n_trades = (turnover > 0).sum()
    total_costs = costs.sum()

    return BacktestResult(
        returns=net_ret, cumulative=cum,
        sharpe=metrics["sharpe"], t_stat=metrics["t_stat"],
        max_drawdown=metrics["max_drawdown"], information_ratio=metrics["ir"],
        turnover=turnover.mean() * 252, total_costs=total_costs, n_trades=n_trades,
    )


def compute_metrics(returns_series: pd.Series) -> dict:
    """Compute the 4 canonical metrics from §7."""
    r = returns_series.dropna()
    n = len(r)
    if n < 2:
        return {"sharpe": 0, "t_stat": 0, "max_drawdown": 0, "ir": 0}

    mean_r = r.mean()
    std_r = r.std()

    sharpe = mean_r / std_r * np.sqrt(252) if std_r > 0 else 0
    t_stat = mean_r / (std_r / np.sqrt(n)) if std_r > 0 else 0

    cum = (1 + r).cumprod()
    peak = cum.cummax()
    dd = (cum - peak) / peak
    max_dd = dd.min()

    # IR (here same as Sharpe if no benchmark; use excess returns for true IR)
    ir = sharpe  # placeholder — override with benchmark-adjusted version

    return {
        "sharpe": round(sharpe, 4),
        "t_stat": round(t_stat, 4),
        "max_drawdown": round(max_dd, 4),
        "ir": round(ir, 4),
    }


def walk_forward(
    signals_fn,
    df: pd.DataFrame,
    returns_col: str,
    train_window: int = 252,
    test_window: int = 63,
    costs_bps: float = 5.0,
) -> pd.DataFrame:
    """Walk-forward backtest. signals_fn(train_df) -> pd.Series of signals."""
    results = []
    n = len(df)
    start = train_window

    while start + test_window <= n:
        train = df.iloc[start - train_window:start]
        test = df.iloc[start:start + test_window]

        try:
            signals = signals_fn(train)
            # Align signals with test returns
            test_signals = signals.reindex(test.index).fillna(0)
            bt = backtest(test_signals, test[returns_col], costs_bps)
            results.append({
                "period_start": test.index[0],
                "period_end": test.index[-1],
                "sharpe": bt.sharpe,
                "return": bt.returns.sum(),
                "max_dd": bt.max_drawdown,
            })
        except Exception as e:
            results.append({
                "period_start": test.index[0],
                "period_end": test.index[-1],
                "sharpe": np.nan, "return": np.nan, "max_dd": np.nan,
            })

        start += test_window

    return pd.DataFrame(results)


if __name__ == "__main__":
    import json
    rng = np.random.default_rng(42)
    idx = pd.date_range("2020-01-01", periods=500, freq="B")
    returns = pd.Series(rng.normal(0.0003, 0.01, 500), index=idx)
    signals = pd.Series(np.sign(rng.normal(0, 1, 500)), index=idx)

    result = backtest(signals, returns, costs_bps=5)
    print(f"Sharpe: {result.sharpe:.2f}, t-stat: {result.t_stat:.2f}")
    print(f"MDD: {result.max_drawdown:.2%}, Turnover: {result.turnover:.1f}x/yr")

    with open("results.json", "w") as f:
        json.dump(compute_metrics(result.returns), f, indent=2)
