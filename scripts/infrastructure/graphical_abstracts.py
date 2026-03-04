"""graphical_abstracts — Compose multi-panel graphical abstracts."""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.image import imread
from pathlib import Path
import numpy as np


def compose_abstract(
    title: str,
    figure_paths: list[str],
    metrics: dict | None = None,
    summary_text: str = "",
    path: str | None = None,
    figsize: tuple = (16, 9),
) -> plt.Figure:
    """Arrange sub-figures + metrics + text into one graphical abstract."""
    n_figs = len(figure_paths)
    n_cols = min(n_figs, 3)
    has_text = bool(metrics or summary_text)

    fig = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(2 if has_text else 1, max(n_cols, 1),
                           height_ratios=[3, 1] if has_text else [1],
                           hspace=0.3, wspace=0.2)

    # Title
    fig.suptitle(title, fontsize=18, fontweight="bold", y=0.98)

    # Sub-figures
    for i, fp in enumerate(figure_paths[:n_cols]):
        ax = fig.add_subplot(gs[0, i])
        if Path(fp).exists():
            img = imread(fp)
            ax.imshow(img)
        ax.axis("off")
        ax.set_title(Path(fp).stem.replace("_", " ").title(), fontsize=10)

    # Metrics / text panel
    if has_text:
        ax_text = fig.add_subplot(gs[1, :])
        ax_text.axis("off")

        text_parts = []
        if metrics:
            metric_str = "  |  ".join(f"{k}: {v}" for k, v in metrics.items())
            text_parts.append(metric_str)
        if summary_text:
            text_parts.append(summary_text)

        ax_text.text(0.5, 0.5, "\n".join(text_parts), ha="center", va="center",
                     fontsize=12, transform=ax_text.transAxes,
                     bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8))

    if path:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close(fig)
    return fig


if __name__ == "__main__":
    compose_abstract(
        title="HYP-001: IG Spread Momentum",
        figure_paths=["figures/time_series.png", "figures/drawdown.png"],
        metrics={"OOS Sharpe": 0.82, "t-stat": 1.91, "MDD": "-4.3%"},
        summary_text="Momentum signal works in low-vol regimes.",
        path="figures/graphical_abstract.png",
    )
    print("Abstract saved.")
