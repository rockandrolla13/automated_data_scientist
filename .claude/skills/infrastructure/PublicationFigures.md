# PublicationFigures

## When to Use
- Any plot saved to `/artifacts/figures/` or experiment `figures/`.
- Journal-quality figures with consistent style.
- Time series, distributions, scatter, heatmaps, correlation matrices.

## Packages
```python
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
```

## Corresponding Script
`/scripts/infrastructure/publication_figures.py`
- `setup_style()` — apply project-wide matplotlib rcParams
- `plot_time_series(df, cols, title, path)` — multi-panel time series
- `plot_distribution(series, title, path)` — histogram + KDE + QQ
- `plot_correlation_matrix(df, title, path)` — lower-triangle heatmap
- `plot_drawdown(returns, title, path)` — cumulative + drawdown subplot
- `save_fig(fig, path, dpi)` — save with tight_layout, default 150dpi

## Gotchas
1. **Call `setup_style()` once per script.** Don't repeat rcParams.
2. **DPI ≥ 150** for any saved figure. 300 for print/LaTeX.
3. **Colorblind-safe palettes.** Use `sns.color_palette("colorblind")` or `"muted"`.
4. **Date formatting.** Use `mdates.AutoDateLocator` + `ConciseDateFormatter` for time axes.
5. **Don't use `plt.show()` in scripts.** Save to file. `plt.show()` is for notebooks only.

## Interpretation Guide
N/A — output skill. Success = clean, readable, correctly labeled figures.

## References
- Tufte, E. (2001). *The Visual Display of Quantitative Information*.
- Matplotlib: https://matplotlib.org/stable/
- Seaborn: https://seaborn.pydata.org/
