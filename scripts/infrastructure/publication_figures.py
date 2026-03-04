"""publication_figures — Journal-quality matplotlib/seaborn figures."""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path


def setup_style() -> None:
    """Apply project-wide figure style. Call once per script."""
    sns.set_palette("colorblind")
    plt.rcParams.update({
        "figure.figsize": (10, 6),
        "figure.dpi": 150,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "font.family": "sans-serif",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.3,
    })


def save_fig(fig: plt.Figure, path: str, dpi: int = 150) -> None:
    """Save figure with tight layout."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_time_series(
    df: pd.DataFrame,
    cols: list[str] | None = None,
    title: str = "",
    path: str | None = None,
    figsize: tuple = (12, 6),
) -> plt.Figure:
    """Multi-line time series plot."""
    setup_style()
    cols = cols or list(df.select_dtypes(include=[np.number]).columns)
    fig, ax = plt.subplots(figsize=figsize)

    for col in cols:
        ax.plot(df.index, df[col], label=col, linewidth=1.0)

    ax.set_title(title)
    ax.legend(loc="best")
    if isinstance(df.index, pd.DatetimeIndex):
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))

    if path:
        save_fig(fig, path)
    return fig


def plot_distribution(
    series: pd.Series,
    title: str = "",
    path: str | None = None,
) -> plt.Figure:
    """Histogram + KDE + normal overlay + stats annotation."""
    setup_style()
    from scipy import stats as sp_stats

    clean = series.dropna()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Histogram + KDE
    ax = axes[0]
    ax.hist(clean, bins=50, density=True, alpha=0.6, color="steelblue", edgecolor="white")
    x = np.linspace(clean.min(), clean.max(), 200)
    ax.plot(x, sp_stats.norm.pdf(x, clean.mean(), clean.std()), "r--", label="Normal", linewidth=1.5)
    ax.set_title(f"{title} Distribution")
    ax.legend()
    stats_text = f"μ={clean.mean():.4f}\nσ={clean.std():.4f}\nskew={clean.skew():.2f}\nkurt={clean.kurtosis():.2f}"
    ax.text(0.97, 0.97, stats_text, transform=ax.transAxes, va="top", ha="right",
            fontsize=9, bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    # QQ plot
    ax = axes[1]
    sp_stats.probplot(clean, dist="norm", plot=ax)
    ax.set_title("Q-Q Plot")

    fig.suptitle(title, fontsize=14, y=1.02)
    if path:
        save_fig(fig, path)
    return fig


def plot_correlation_matrix(
    df: pd.DataFrame,
    title: str = "Correlation Matrix",
    path: str | None = None,
) -> plt.Figure:
    """Lower-triangle heatmap."""
    setup_style()
    corr = df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
                center=0, vmin=-1, vmax=1, ax=ax, square=True)
    ax.set_title(title)

    if path:
        save_fig(fig, path)
    return fig


def plot_drawdown(
    returns: pd.Series,
    title: str = "Cumulative Return & Drawdown",
    path: str | None = None,
) -> plt.Figure:
    """Cumulative returns + drawdown subplot."""
    setup_style()
    cum = (1 + returns).cumprod()
    peak = cum.cummax()
    dd = (cum - peak) / peak

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True,
                                     gridspec_kw={"height_ratios": [3, 1]})

    ax1.plot(cum.index, cum, color="steelblue", linewidth=1.0)
    ax1.set_title(title)
    ax1.set_ylabel("Cumulative Return")

    ax2.fill_between(dd.index, dd, 0, color="salmon", alpha=0.7)
    ax2.set_ylabel("Drawdown")
    ax2.set_xlabel("Date")

    if path:
        save_fig(fig, path)
    return fig


if __name__ == "__main__":
    CONFIG = {
        "data_source": "../../data/returns_clean.parquet",
        "output_dir": "figures/",
    }

    df = pd.read_parquet(CONFIG["data_source"])
    setup_style()

    plot_time_series(df, title="Price Series", path=f"{CONFIG['output_dir']}/time_series.png")
    for col in df.select_dtypes(include=[np.number]).columns[:3]:
        plot_distribution(df[col], title=col, path=f"{CONFIG['output_dir']}/dist_{col}.png")
    plot_correlation_matrix(df, path=f"{CONFIG['output_dir']}/correlation.png")
